# This file controls the low level light stuff
import asyncio

class LightSequence:
    """controls what colors are sent to the array of pixels"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        self.lights = lights
        self.lRange = lRange
        self.distance = distance
        self.strength = strength
        self.stop = False
        return

    def run(self):
        return True

class Stop():
    def __init__(self) -> None:
        self.stop = True
        pass

    def run(self):
        return False

    

class Idle(LightSequence):
    """Sequence that turns the lights off."""

    def __init__(self, lights, lRange):
        super().__init__(lights, lRange)

    def run(self):
        return 


class IdleSky(LightSequence):
    """Twinkling stars for the idle sky"""

    def __init__(self, lights, lRange):
        super().__init__(lights, lRange)
    

class Ground(LightSequence):
    """The ground. can add functionality, but for now is green and blue"""

    def __init__(self, lights, lRange):
        super().__init__(lights, lRange)
    


class Mars(LightSequence):
    def __init__(self, lights, lRange):
        super().__init__(lights, lRange)


    
    