import asyncio
from lights import *
from dsn import *

class Pulse:
    def __init__(self,numLeds):
        """Sets up the lights array and the async queue"""
        self.lights = [0] * numLeds

        # Create an empty queue for our instructions to be stored in
        self.queue = asyncio.Queue(maxsize=200)

        #self.queue.put_nowait()


    async def start(self):
        """start both threads, and wait for them to finish before ending."""
        await asyncio.gather(
            self.runDsn(self.queue),
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


    async def runLights(self, queue):
        """Runs the lights thread. Ideally refreshes the lights quickly (0.1s)
        If queue is empty, runs the idle light pattern
        if queue has items, will read the item and display its pattern
        calls the LightPattern.run() function
        reads a stop item in the queue and ends
        """

        # we know the first value will be the random start location
        prev = await queue.get()
        running = True

        while running:
            # reads the commands in the queue
            # if the queue is currently empty, it will wait for the next item to be added.
            obj = await queue.get()
            if obj is None:
                continue

        return
    
    async def stop(self):
        """calls the stop function in dsn to cascade everything off"""
        pass

    
# This is the section of the program that runs when executed
if __name__ == "__main__":
    numlights = 30

    # create the parser
    p = Pulse(numlights)

    # start the job.
    # this is a blocking call and will not move forward until finished
    asyncio.run(p.start())
