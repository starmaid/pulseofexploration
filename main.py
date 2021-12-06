import asyncio
from lights import *
from dsn import *

class runner:
    def __init__(self):
        # This function runs when the class is instantiated

        # Create an empty queue for our instructions to be stored in
        self.queue = asyncio.Queue(maxsize=200)

        # tell the machine that the starting point is somewhere random on the bed
        #self.queue.put_nowait()


    async def start(self):
        # start both threads, and wait for them to finish before ending.
        await asyncio.gather(
            self.getDsn(self.queue),
            self.processLights(self.queue)
            )
        return

    async def getDsn(self, queue):
        # this thread manages reading the file.
        # we only have so much memory on a control board (like 64k)
        # so we cannot load the entire file.
        totalLines = 0

        while True:
            while queue.full():
                # if queue is full, wait for a bit
                await asyncio.sleep(0.1)

            

            # now add that object to the queue
            await self.queue.put(obj)
            totalLines += 1

        # put the "end job object in the queue
        await self.queue.put(endJob())
        return


    async def processLights(self, queue):
        # This one is a loop that sends the commands to the motors and
        # waits for them to complete. This thread will process commands as
        # they are added by the reading thread.

        # we know the first value will be the random start location
        prev = await queue.get()
        running = True
        total = 0

        while running:
            # reads the commands in the queue
            # if the queue is currently empty, it will wait for the next item to be added.
            obj = await queue.get()
            total = total + 1
            if obj is None:
                continue

            # execute the command
            # if it returns false, then the job has ended.
            running = await obj.execute(prev)

            # save the points into an array so we can look at them
            self.points.append(obj.getCoordinates())

            # move to the next one
            prev = obj
        return
    

    
# This is the section of the program that runs when executed
if __name__ == "__main__":
    # create the parser
    p = runner()

    # start the job.
    # this is a blocking call and will not move forward until finished
    asyncio.run(p.start())
