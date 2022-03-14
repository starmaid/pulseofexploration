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

    def __init__(self, lights, lRange, ship=None):
        self.lights = lights
        self.lRange = lRange
        self.ship = ship
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

    def __init__(self, lights, lRange, ship=None):
        super().__init__(lights, lRange, ship)

    def run(self):
        """Fill section of the lights array with (0,0,0)"""
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,0,0) for i in range(self.lRange[0],self.lRange[1])]
            self.progress = 1
        
        return True


class Transmission(LightSequence):
    """Sequence that plays for the signal"""

    def __init__(self, lights, lRange, ship=None):
        super().__init__(lights, lRange, ship)
        # set parameters for how things should be represented

        # up vs down determines which direction/sign stuff
        if ship['down']:
            self.dir = 'down'
        elif ship['up']:
            self.dir = 'up'
        else:
            # i hope we never get here
            self.dir = None


        # round trip light time (s)
        # from 0 to 200000 (leo to voyager) with -1.0 as None
        # probably do some log scaling
        if self.ship['rtlt'] == -1:
            self.rtlt = 10
        else:
            self.rtlt = self.ship['rtlt']


        # power
        # down values are in dBm, up in kW, keyerror if none
        # change brightness of lights
        if 'power' in self.ship.keys():
            if self.dir == 'down':
                self.power = 10 ** ((self.ship['power'] - 30) / 10) / 1000
            else:
                self.power = self.ship['power']
        else:
            self.power = 0.2


        # frequency
        # up is in Hz, down is in MHz, keyerror if none
        # change spacing of lights
        if 'frequency' in self.ship.keys():
            if self.dir == 'up':
                self.frequency = self.ship['frequency'] / 1000000000
            else:
                self.frequency = self.ship['frequency']
        else:
            self.frequency = 200


        # send 10 beams or something idk
        # this could be datarate



    def run(self):


        self.progress += 1
        return 


class IdleSky(LightSequence):
    """Twinkling stars for the idle sky"""

    def __init__(self, lights, lRange, ship=None):
        super().__init__(lights, lRange, ship)
        
    
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
    def __init__(self, lights, lRange, ship=None):
        super().__init__(lights, lRange, ship)
    
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

    def __init__(self, lights, lRange):
        super().__init__(lights, lRange)
    
    def run(self):
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,255,0) for i in range(self.lRange[0],self.lRange[1])]
        return True

class Img(LightSequence):
    def __init__(self, lights, lRange, theme, filename, ship=None):
        super().__init__(lights, lRange, ship)
        self.stop = not self.openImg(theme + '/' + filename + '.png')
    
    def run(self):
        return self.playImg()

    
    