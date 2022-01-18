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
        """Run should return true until the animation is done playing"""
        return


class Stop():
    def __init__(self) -> None:
        self.stop = True
        pass

    def run(self):
        return False

    

class Idle(LightSequence):
    """Sequence that turns the lights off."""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)

    def run(self):
        return 


class Transmission(LightSequence):
    """Sequence that plays for the signal"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    
    def run(self):
        return


class IdleSky(LightSequence):
    """Twinkling stars for the idle sky"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    

class DeepSpace(LightSequence):
    """deep space twinkle"""
    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    

class Ground(LightSequence):
    """The ground. can add functionality, but for now is green and blue"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    


class Mars(LightSequence):
    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)

    
    