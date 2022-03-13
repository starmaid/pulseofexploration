# This file controls the low level light stuff
import asyncio
import random
import logging

from PIL import Image

logging.getLogger("PIL").setLevel(logging.WARNING)

#import board
#import neopixel

# Setup Lines
random.seed()
IMAGESPATH = "./data/"


class LightSequence:
    """controls what colors are sent to the array of pixels"""

    def __init__(self, lights, lRange, ship=None, distance=None, strength=None):
        self.lights = lights
        self.lRange = lRange
        self.ship = ship
        self.distance = distance
        self.strength = strength
        self.stop = False
        self.progress = 0
        return
    
    def openImg(self,imgname):
        try:
            self.im = Image.open(IMAGESPATH + imgname, 'r')
        except:
            raise IOError('Problem loading image \"' + imgname + '\"')
        mode = self.im.mode
        if mode not in ['RGB', 'RGBA']:
            raise IOError('File \"' + imgname + '\" is not opening in RGB or RGBA mode. Please make sure file is saved in an appropriate format (like png)')
        return True
    
    def getRow(self, image, row, numPixels):
        width,height = image.size
        isvalid = row*width < width*height
        if not isvalid:
            return False
        rpix = list(image.getdata())[(width*row):(width*(row+1))]
        #print([x[0] for x in rpix])
        rout = [rpix[self.vmap(n,0,numPixels,0,width)][0:3] for n in range(0,numPixels)]
        return rout

    def vmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows."""
        y = (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
        return int(y)

    def playImg(self):
        """Play an image row by row on the lights."""
        rout = self.getRow(self.im, self.progress, self.lRange[1]-self.lRange[0])
        if not rout:
            return False
        else:
            #print([x[0] for x in rout])
            self.lights[self.lRange[0]:self.lRange[1]] = rout
            self.progress += 1
        return True

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

    def __init__(self, lights, lRange, ship=None, distance=None, strength=None):
        super().__init__(lights, lRange, ship, distance, strength)

    def run(self):
        """Fill section of the lights array with (0,0,0)"""
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,0,0) for i in range(self.lRange[0],self.lRange[1])]
            self.progress = 1
        
        return True


class Transmission(LightSequence):
    """Sequence that plays for the signal"""

    def __init__(self, lights, lRange, ship=None, distance=None, strength=None):
        super().__init__(lights, lRange, ship, distance, strength)
        

    def run(self):

        return 


class IdleSky(LightSequence):
    """Twinkling stars for the idle sky"""

    def __init__(self, lights, lRange, ship=None, distance=None, strength=None):
        super().__init__(lights, lRange, ship, distance, strength)
        
    
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
    def __init__(self, lights, lRange, ship=None, distance=None, strength=None):
        super().__init__(lights, lRange, ship, distance, strength)
    
    def run(self):
        """FASTER turns one random light on, fades every light that is currently on"""
        s = 15
        for i in range(self.lRange[0],self.lRange[1]):
            b = self.lights[i][0]
            if b > 0:
                c = b - s
                if c < 0:
                    self.lights[i] = (0,0,0)
                else:
                    self.lights[i] = (c,c,c)
        
        if self.progress % 5 == 0:
            j = random.randrange(self.lRange[0],self.lRange[1])
            self.lights[j] = (255,255,255)

        self.progress += 1

        if self.progress < 20:
            return True
        else:
            return False
    

class Ground(LightSequence):
    """The ground. can add functionality, but for now is green and blue"""

    def __init__(self, lights, lRange, distance=None, strength=None):
        super().__init__(lights, lRange, distance, strength)
    
    def run(self):
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,255,0) for i in range(self.lRange[0],self.lRange[1])]
        return True

class Img(LightSequence):
    def __init__(self, lights, lRange, theme, filename, ship=None, distance=None, strength=None):
        super().__init__(lights, lRange, ship, distance, strength)
        self.stop = not self.openImg(theme + '/' + filename + '.png')
    
    def run(self):
        return self.playImg()

    
    