# main.py
# Written by Starmaid in early 2022

# Builtin Libraries
import asyncio
import json
from msilib.schema import Error
import platform
import logging
from datetime import datetime

# Determine if we should enter debug mode
if 'arm' in platform.machine():
    # then we are running on a board that can do lights. probably
    live = True
    import board
    import neopixel
    logfilename = str(datetime.now())[0:10] + '.log'
    logging.basicConfig(filename=logfilename, format='%(asctime)s %(levelname)s %(message)s', level=logging.WARNING)
else:
    live = False
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)



# Custom modules
import dsn
import lights


class Pulse:
    def __init__(self):
        """Sets up the config, lights array, and the async queue"""

        # Load the config file with ship/planet associations
        try:
            with open("./data/config.json","r") as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error('Error loading config file: ' + str(e))
            logging.error('Stopping Program')
            raise

        try:
            self.themeName = self.config['theme']
            with open("./data/" + str(self.themeName) + "/theme.json","r") as f2:
                self.theme = json.load(f2)
        except Exception as e:
            logging.error('Error loading theme: ' + str(e))
            logging.error('Stopping Program')
            raise

        numLeds = [self.config['lights'][a] for a in ['ground', 'signal', 'sky']]
        
        global live
        if live:
            ORDER = neopixel.GRB
            self.lights = neopixel.NeoPixel(board.D18, sum(numLeds), brightness=0.2, auto_write=False, pixel_order=ORDER)
        else:
            self.lights = [(0,0,0)] * sum(numLeds)

        # tuple ranges for each section so we can pass them to sequences
        self.ground = (0, numLeds[0])
        self.signal = (numLeds[0], numLeds[0]+numLeds[1])
        self.sky = (numLeds[0]+numLeds[1], sum(numLeds))

        # list of currently active sequences
        self.activeSequences = [None, None, None]

        # Create an empty queue for our instructions to be stored in
        self.queue = asyncio.Queue(maxsize=50)

        #self.queue.put_nowait()


    async def start(self):
        """start both threads, and wait for them to finish before ending."""
        # self.runDsn(self.queue),
        await asyncio.gather(
            self.runDsn(self.queue),
            self.runSequenceQueue(self.queue),
            self.runLights(self.queue)
            )
        return

    async def runDsn(self, queue):
        """handles periodically updating from dsn now
        and places new light patterns in the queue
        reads when the dsn sends a stop item, sends it to lights, and ends."""

        q = dsn.DSNQuery()
        
        running = True

        while running:
            try:
                newsignals = q.getNew()

                if len(newsignals) > 0:
                    # put the new objects in
                    for s in newsignals:
                        newSequence = None
                        if s in self.theme['ships'].keys():
                            locname = self.theme['ships'][s]

                            logging.debug('%s loading %s from theme', s, locname)

                            try:
                                # Attempt to load the class from lights.py
                                classname = getattr(lights,locname)
                                newSequence = classname(self.lights,self.sky)
                                logging.debug('Found LightSequence class ', classname)
                            except AttributeError:
                                # If that that class doesnt exist, load that image
                                logging.debug('LightSequence Class not found. Loading image file')
                                newSequence = lights.Img(self.lights,self.sky,self.themeName,locname)
                            

                        else:
                            logging.debug('%s not found in config, loading DeepSpace')
                            newSequence = lights.DeepSpace(self.lights,self.sky)

                        await self.queue.put(newSequence)

                await asyncio.sleep(5)
                
            except KeyboardInterrupt:
                # Add the stop object
                running = False
                self.queue.put(lights.Stop())
        return

    async def runSequenceQueue(self, queue):
        """Manages the queue of light effects and places them in self.activeSequences
        If queue is empty, runs the idle light pattern
        if queue has items, will read the item and display its pattern
        calls the LightPattern.run() function
        reads a stop item in the queue and ends
        """

        # set the startup running sequences
        self.activeSequences = [lights.Ground(self.lights,self.ground), 
                            lights.Idle(self.lights,self.signal), 
                            lights.IdleSky(self.lights,self.sky)]


        #prev = await queue.get()
        running = True

        while running:
            # reads the commands in the queue
            # if the queue is currently empty, it will wait for the next item to be added.
            obj = await queue.get()
            if obj is not None:
                if obj.stop:
                    running = False
                    self.activeSequences = [obj,obj,obj]
                else:
                    self.activeSequences[2] = obj
                    self.activeSequences[1] = lights.Transmission(self.lights,self.signal)
                    print('\nNew sequence')
                    # set the sky as the new sky
                    # set the signal parameters and add
            
            # Because this is just placing different objects in the queue
            # It can run at a lower clock speed than the framerate
            await asyncio.sleep(1)
        return

    async def runLights(self, queue):
        """Runs the lights thread. Ideally refreshes the lights quickly (0.1s)"""

        running = True

        while running:
            if self.activeSequences[0].stop:
                running = False
                break
            
            # The ground should never end LOL
            self.activeSequences[0].run()

            cont = self.activeSequences[1].run()
            if not cont:
                self.activeSequences[1] = lights.Idle(self.lights,self.signal)
                logging.debug('End of signal sequence')

            cont = self.activeSequences[2].run()
            if not cont:
                self.activeSequences[2] = lights.IdleSky(self.lights,self.sky)
                logging.debug('End of sky sequence')

            if live:
                self.lights.show()
            else:
                print(str([self.lights[a][0] for a in range(0,len(self.lights))]) + '\r',end='')
            
            await asyncio.sleep(0.1)
        return
    

    
# This is the section of the program that runs when executed
if __name__ == "__main__":
    # create the parser
    p = Pulse()

    # start the job.
    # this is a blocking call and will not move forward until finished
    asyncio.run(p.start())
