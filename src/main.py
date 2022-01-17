import asyncio

#import board
#import neopixel

from dsn import *
from lights import *


class Pulse:
    def __init__(self,numLeds):
        """Sets up the lights array and the async queue"""
        #ORDER = neopixel.GRB
        #self.lights = neopixel.NeoPixel(board.D18, sum(numLeds), brightness=0.2, auto_write=False, pixel_order=ORDER)
        self.lights = [(0,0,0)] * sum(numLeds)

        # ranges for each section so we can pass them to sequences
        self.ground = (0, numLeds[0]-1)
        self.signal = (numLeds[0], numLeds[0]+numLeds[1]-1)
        self.sky = (numLeds[0]+numLeds[1], sum(numLeds)-1)

        # list of currently active sequences
        self.activeSequences = [None, None, None]

        # Create an empty queue for our instructions to be stored in
        self.queue = asyncio.Queue(maxsize=200)

        #self.queue.put_nowait()


    async def start(self):
        """start both threads, and wait for them to finish before ending."""
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

        # now add that object to the queue
        # await self.queue.put()

        # put the "end job object in the queue
        # await self.queue.put(endJob())
        return

    async def runSequenceQueue(self, queue):
        """Manages the queue of light effects and places them in self.activeSequences
        If queue is empty, runs the idle light pattern
        if queue has items, will read the item and display its pattern
        calls the LightPattern.run() function
        reads a stop item in the queue and ends
        """

        prev = await queue.get()
        running = True

        while running:
            # reads the commands in the queue
            # if the queue is currently empty, it will wait for the next item to be added.
            obj = await queue.get()
            if obj is None:
                continue

            asyncio.sleep(0.1)
        return

    async def runLights(self, queue):
        """Runs the lights thread. Ideally refreshes the lights quickly (0.1s)"""

        running = True

        while running:
            running = self.updateSequences()
            asyncio.sleep(0.1)
            self.lights.show()
        return
    

    def updateSequences(self):
        """tells each of the active sequenecs to update their lights"""
        pass
    
    async def stop(self):
        """calls the stop function in dsn to cascade everything off"""
        pass

    
# This is the section of the program that runs when executed
if __name__ == "__main__":
    numlights = [10,10,10]

    # create the parser
    p = Pulse(numlights)

    # start the job.
    # this is a blocking call and will not move forward until finished
    asyncio.run(p.start())
