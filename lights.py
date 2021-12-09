# This file controls the low level light stuff
import asyncio

class lightDriver:
    """Handles sending commands over the PWM pin to the lights
    Manages timing and stuff"""

    def __init__(self, cmd):
        return

    async def execute(self, prev):

        await asyncio.sleep()
        return True


# have a class for all animations that we can inherit?

# Have a class for each animation? that way we can send characteristics
# of a dsn query and it will be supre easy

class idle:
    def __init__(self):
        return
    