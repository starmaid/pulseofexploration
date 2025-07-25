# main.py
# Written by Starmaid in early 2022

# Builtin Libraries
import asyncio
import json
import platform
import logging
import traceback
from datetime import datetime

# Set library logging levels
logging.getLogger("asyncio").setLevel(logging.WARNING)

# Determine if we should enter live or debug mode
if 'arm' in platform.machine():
    arm = True
    # Then we are running on a board that can do lights. probably
    logfilename = str(datetime.now())[0:10] + '.log'
    logging.basicConfig(filename=logfilename, format='%(asctime)s %(levelname)s %(message)s', level=logging.WARNING)
    print('Running on ARM CPU, likely raspberry pi')
    logging.warning('Running on ARM CPU')
else:
    arm = False
    # Then we are probably not running on a RPi.
    logging.basicConfig(format='%(message)s', level=logging.DEBUG)
    logging.warning('Not running on ARM CPU')

# Custom modules
import dsn
import lights_patterns as lights_patterns
from lights.lights import NeopixelRPILightStrip, WledLightStrip, PrintTestLightStrip

# one global variable
# its set in one location and read in another. thread safe.
lights_on_override = True

class Pulse:
    def __init__(self):
        """Sets up the config, lights array, and the async queue"""

        # Try to load the config file
        try:
            with open("./data/config.json","r") as f:
                self.config = json.load(f)
        except Exception as e:
            logging.error('Error loading config file: ' + str(e))
            logging.error('Stopping Program')
            raise e
            
        try:
            # Loading all values from config
            self.lightsegments = self.config['lights']
            self.lights_type = self.config['lights_type']
            if self.lights_type not in self.config['_lights_type_options']:
                raise ValueError(f"Lights type {self.lights_type} not a valid option.")

            self.neopixel_pin = self.config['Neopixel_pin']
            self.wled_ip = self.config['Wled_IP']
            self.brightness = self.config['brightness']
            self.rgbw = self.config['RGBW']
            self.groundfirst = self.config['groundFirst']
            self.framerate = self.config['framerate']
            self.themeName = self.config['theme']
            self.lat = self.config['latitude']
            self.lng = self.config['longitude']
            self.netswitch = self.config['expose_net_switch']
            if self.netswitch:
                self.netswitch_port = self.config['expose_net_port']
            else:
                self.netswitch_port  = None
        except Exception as e:
            logging.error('Value not found in config file: ' + str(e))
            logging.error('Stopping Program')
            raise e
        
        if self.brightness > 100 or self.brightness < 0:
            logging.warning('Brightness not between 0 and 100: ' + str(self.brightness))
            logging.warnin('Setting brightness to 20%')
            self.brightness = 20

        self.brightness = self.brightness / 100

        # Try to open themes
        try:
            with open("./data/" + str(self.themeName) + "/theme.json","r") as f2:
                self.theme = json.load(f2)
        except Exception as e:
            logging.error('Error loading theme: ' + str(e))
            logging.error('Stopping Program')
            raise e

        numLeds = [self.lightsegments[a] for a in ['ground', 'signal', 'sky']]
        
        # Set up LED control, if we are live
        self.lights_strip = [(0,0,0)] * sum(numLeds)
        if self.lights_type == "NeopixelRPILightStrip":
            if self.rgbw:
                order = "GRBW"
            else:
                order = "GRB"
            try:
                
                self.lights_object = NeopixelRPILightStrip(sum(numLeds), self.neopixel_pin, order, self.brightness)
            except Exception as e:
                logging.error('Error setting up lights: ' + str(e))
                logging.error('Stopping Program')
                raise e
        elif self.lights_type == "PrintTestLightStrip":
            self.lights_object = PrintTestLightStrip(sum(numLeds))
        elif self.lights_type == "WledLightStrip":
            self.lights_object = WledLightStrip(sum(numLeds),self.wled_ip)


        # Tuple ranges for each section so we can pass them to sequences
        # always increasing (first element < second element)
        # first inclusing, second exclusive
        if self.groundfirst:
            self.ground = (0, numLeds[0])
            self.signal = (numLeds[0], numLeds[0]+numLeds[1])
            self.sky = (numLeds[0]+numLeds[1], sum(numLeds))
        else:
            self.sky = (0, numLeds[2])
            self.signal = (numLeds[2], numLeds[2]+numLeds[1])
            self.ground = (numLeds[2]+numLeds[1], sum(numLeds))

        # list of currently active sequences
        self.activeSequences = [None, None, None]

        # Turn framerate into a number of seconds
        self.framedelay = 1 / int(self.framerate)

        # Create an empty queue for our instructions to be stored in
        self.queue = asyncio.Queue(maxsize=50)

    async def start(self):
        """start both threads, and wait for them to finish before ending."""

        await asyncio.gather(
                self.runDsn(self.queue),
                self.runSequenceQueue(self.queue),
                self.runLights(self.queue),
                self.runSwitchServer(),
                return_exceptions=False
                )
        
        return
    
    async def handle_client(self,reader,writer):
        global lights_on_override
        message = await reader.read(1024)
        logging.debug(f'tcp rcv: {message}')
        m = message.decode().strip().upper()

        if m == 'ON':
            logging.debug("tcp command: ON")
            lights_on_override = True
            writer.write(b'OK')
        elif m == 'OFF':
            logging.debug("tcp command: OFF")
            lights_on_override = False
            writer.write(b'OK')
        elif m == 'STATUS':
            if lights_on_override:
                writer.write(b'ON')
            else:
                writer.write(b'OFF')
        else:
            logging.debug(f"tcp command: bad")
            writer.write(b'BAD CMD')
        
        await writer.drain()
        writer.close()
        await writer.wait_closed()


    async def runSwitchServer(self):
        if not self.netswitch:
            return
        self.server = await asyncio.start_server(
            self.handle_client, 
            '', 
            self.netswitch_port)
        
        async with self.server:
            await self.server.serve_forever()
        

    async def runDsn(self, queue):
        """handles periodically updating from dsn now
        and places new light patterns in the queue
        reads when the dsn sends a stop item, sends it to lights, and ends."""

        q = dsn.DSNQuery()
        running = True

        while running:
            try:
                # Poll DSN
                newsignals = q.getNew().keys()

                # Check if theres anything new
                if len(newsignals) > 0:
                    for s in newsignals:
                        newSequence = None
                        if s in self.theme['ships'].keys():
                            locname = self.theme['ships'][s]

                            logging.debug('%s loading %s from theme', s, locname)

                            try:
                                # Attempt to load the class from lights.py
                                classname = getattr(lights_patterns,locname)
                                newSequence = classname(self.lights_strip, self.sky, ship=q.activeSignals[s])
                                logging.debug('Found LightSequence class ', classname)
                            except AttributeError:
                                # If that that class doesnt exist, load that image
                                logging.debug('LightSequence Class not found. Loading image file')
                                newSequence = lights_patterns.Img(self.lights_strip, self.sky, 
                                        self.themeName,locname,ship=q.activeSignals[s])
                            

                        else:
                            logging.debug('%s not found in config, loading DeepSpace',s)
                            newSequence = lights_patterns.DeepSpace(self.lights_strip,self.sky,ship=q.activeSignals[s])

                        await self.queue.put(newSequence)

                await asyncio.sleep(30)
                
            except KeyboardInterrupt:
                # Add the stop object
                # TODO: this doesnt really work either
                running = False
                self.queue.put(lights_patterns.Stop())
        return

    async def runSequenceQueue(self, queue):
        """Manages the queue of light effects and places them in self.activeSequences
        If queue is empty, runs the idle light pattern
        if queue has items, will read the item and display its pattern
        calls the LightPattern.run() function
        reads a stop item in the queue and ends
        """

        # Set the startup running sequences
        self.activeSequences = [lights_patterns.Ground(self.lights_strip,self.ground,self.lat,self.lng), 
                            lights_patterns.Idle(self.lights_strip,self.signal), 
                            lights_patterns.IdleSky(self.lights_strip,self.sky)]

        running = True

        self.sequencePlaying = False

        while running:
            # Reads the commands in the queue
            # If the queue is currently empty, it will wait for the next item to be added.
            if not self.sequencePlaying:
                obj = await queue.get()
                if obj is not None:
                    if obj.stop:
                        running = False
                        self.activeSequences = [obj,obj,obj]
                    else:
                        self.sequencePlaying = True
                        self.activeSequences[2] = obj
                        try:
                            pass
                            #print(obj.ship['up_power'])
                        except:
                            pass
                        self.activeSequences[1] = lights_patterns.Transmission(self.lights_strip,self.signal,ship=obj.ship,groundfirst=self.groundfirst)
                        #print('\nNew sequence')
                        # set the sky as the new sky
                        # set the signal parameters and add
            
            # Because this is just placing different objects in the queue
            # It can run at a lower clock speed than the framerate
            await asyncio.sleep(1)
        return

    async def runLights(self, queue):
        """Runs the lights thread. Ideally refreshes the lights quickly (0.1s)"""

        running = True

        global lights_on_override

        while running:
            if True in [s.stop for s in self.activeSequences]:
                running = False
            
            # The ground should never end LOL
            self.activeSequences[0].run()

            cont = self.activeSequences[1].run()
            if not cont:
                self.activeSequences[1] = lights_patterns.Idle(self.lights_strip,self.signal)
                logging.debug('End of signal sequence')
                self.sequencePlaying = False

            cont = self.activeSequences[2].run()
            if not cont:
                self.activeSequences[2] = lights_patterns.IdleSky(self.lights_strip,self.sky)
                logging.debug('End of sky sequence')

            if not lights_on_override:
                #logging.debug('blocked by udp packet switch')
                # do not replace reference to self.lights_strip! modify in place
                for i in range(len(self.lights_strip)):
                    self.lights_strip[i] = (0,0,0)

            self.lights_object.setLights(self.lights_strip)
            
            # Wait frame time to refresh lights
            await asyncio.sleep(self.framedelay)
        return
    

    
# This is the section of the program that runs when executed
if __name__ == "__main__":
    p = Pulse()

    exitWithError = False

    # start the job.
    # this is a blocking call and will not move forward until finished
    try:
        if arm:
            # For some reason this is required on the rpi??
            # python 3.7
            asyncio.get_event_loop().run_until_complete(p.start())
        else:
            # But on windows with python 3.10 gives depreciation warning and wants this
            asyncio.run(p.start())
    except KeyboardInterrupt:
        logging.error('\n\nExiting due to KeyboardInterrupt\n')
        # must modify in place! or else lights will break
        for i in range(len(p.lights_strip)):
            p.lights_strip[i] = (0,0,0)
        p.lights_object.setLights(p.lights_strip)
    except Exception as e:
        logging.exception(f'\n\nError {e.__class__} during lights:\n{e}')
        exitWithError = True
    
    if exitWithError:
        try:
            p.lights_strip = [(0,0,0) for i in range(0,len(p.lights_strip))]
            p.lights_strip[0] = (0,100,0)
            print(p.lights_strip)
            p.lights_object.setLights(p.lights_strip)
        except Exception as e:
            logging.exception(f"Unable to play error lights:\n{e}")
