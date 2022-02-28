# This file controls the low level light stuff
import asyncio
from functools import lru_cache
import random

from PIL import Image

#import board
#import neopixel

# Setup Lines
random.seed()
IMAGESPATH = "./data/"


class LightSequence:
    """controls what colors are sent to the array of pixels"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        self.lights = lights
        self.lRange = lRange
        self.distance = distance
        self.strength = strength
        self.stop = False
        self.progress = 0
        return
    
    def getRow(self, image, row, numPixels):
        width,height = image.size
        isvalid = row*width < width*height
        if not isvalid:
            return False
        rpix = list(image.getdata())[width*row:width*(row+1)]

        rout = [rpix[self.vmap(n,0,width,0,numPixels)] for n in range(0,numPixels)]

        return rout

    def vmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows."""
        return int((x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin)

    def run(self):
        """Run should return true until the animation is done playing"""
        return True


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
        """Fill section of the lights array with (0,0,0)"""
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,0,0) for i in range(self.lRange[0],self.lRange[1])]
            self.progress = 1
        
        return True


class Transmission(LightSequence):
    """Sequence that plays for the signal"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    
    def run(self):
        if self.progress < self.lRange[1]-self.lRange[0]:
            # set all to off
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,0,0) for i in range(self.lRange[0],self.lRange[1])]
            # set just one on
            self.lights[self.lRange[1]-self.progress] = (255,255,255)
            self.progress += 1
            return True
        else:
            return False


class IdleSky(LightSequence):
    """Twinkling stars for the idle sky"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
        
    
    def run(self):
        """turns one random light on, fades every light that is currently on"""
        s = 15
        for i in range(self.lRange[0],self.lRange[1]):
            b = self.lights[i][0]
            if b > 0:
                c = b - s
                if c < 0:
                    self.lights[i] = (0,0,0)
                else:
                    self.lights[i] = (c,c,c)
        
        self.progress += 1

        if self.progress == 10:
            j = random.randrange(self.lRange[0],self.lRange[1])
            self.lights[j] = (255,255,255)
            self.progress = 0
        
        return True
    

class DeepSpace(LightSequence):
    """deep space twinkle"""
    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    

class Ground(LightSequence):
    """The ground. can add functionality, but for now is green and blue"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    
    def run(self):
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,255,0) for i in range(self.lRange[0],self.lRange[1])]
        return True
    


class Mars(LightSequence):
    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
        
        self.im = Image.open(IMAGESPATH + 'Mars.png', 'r')
        
    
    def run(self):
        rout = self.getRow(self.im, self.progress, self.lRange[1]-self.lRange[0])
        print(rout)
        if not rout:
            return False
        else:
            self.lights[self.lRange[0]:self.lRange[1]] = rout
            self.progress += 1
        return True

    
    