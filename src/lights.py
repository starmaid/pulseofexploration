# This file controls the low level light stuff
import asyncio
from pickletools import long4
import random
import logging
import math as m

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
        rout = [rpix[self.linmap(n,0,numPixels,0,width)][0:3] for n in range(0,numPixels)]
        return rout

    def linmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows."""
        y = (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
        return int(y)

    def logmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows."""
        try:
            x = m.log10(x)
        except:
            print('math exception ' + str(x))
            x = 1
        inMin = m.log10(inMin)
        inMax = m.log10(inMax)

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

    def __init__(self, lights, lRange, ship=None, groundfirst=True):
        super().__init__(lights, lRange, ship)
        # set parameters for how things should be represented
        self.groundfirst = groundfirst

        # up vs down determines which direction/sign stuff
        if ship['down'] and ship['up']:
            self.dir = 'both'
        elif ship['up']:
            self.dir = 'up'
        elif ship['down']:
            self.dir = 'down'
        else:
            # i hope we never get here
            self.dir = None

        print(self.dir)

        #with open('./dataout.csv', 'a') as f:
        #    line = ''
        #    for field in ['name', 'rtlt', 'up', 'up_power', 'up_dataRate', 'up_frequency', 'down', 'down_power', 'down_dataRate', 'down_frequency']:
        #        try:
        #            line += str(self.ship[field])
        #        except:
        #            line += 'None'
        #        line += ', '
        #    line += '\n'
        #    f.writelines(line)

        # round trip light time (s)
        # from 0 to 200000 (leo to voyager) with -1.0 as None
        # probably do some log scaling
        if self.ship['rtlt'] == -1:
            self.rtlt = 10
        else:
            self.rtlt = self.ship['rtlt']


        if self.dir in ['down', 'both']:
            # power
            # down values are in dBm, keyerror if none
            # change brightness of lights
            # 2.426920219828798e-22
            # 3.9451198380957787e-22
            # 7.882799856329301e-19
            # 1.1014518076312253e-17
            # 1.5212020429833592e-18
            # 1.0274246946691201e-17
            # 1.263283139977561e-18
            # 4.851862671789916e-18
            # 1.5398481656110987e-18
            print('power (dBm): ' + str(self.ship['down_power']))
            if self.ship['down_power'] == 0:
                self.power = 1
            else:
                self.power = 10 ** ((self.ship['down_power'] - 30) / 10) / 1000
                # now its gunna be super small soooo
                print('power (KW): ' + str(self.power))
                self.power = self.power * 1e22
                if self.power < 1:
                    self.power = 1
            
            # frequency
            # down is in MHz, keyerror if none
            # change spacing of lights
            # 8.420392184740615
            # 8.445743892618303
            # 2.270410574663693
            # 2.281895275773722
            # 8.439690878445852
            # 2.2450060852689053
            # 2.2783730883865863
            # 8.446086418383214
            # 8.439636400350302
            if 'down_frequency' in self.ship.keys() and self.ship['down_frequency'] is not None:
                self.frequency = self.ship['down_frequency'] / 1000000000
            else:
                self.frequency = 8

        elif self.dir == 'up':
            # power
            # up in kW, keyerror if 
            # 4.9
            # 0.26
            # 1.8
            # 9.94
            # 0.21
            # 10.24
            if self.ship['up_power'] == 0:
                self.power = 0.2 * 1000
            else:
                self.power = self.ship['up_power'] * 1000

            # frequency
            # up is in Hz, keyerror if none
            # 7188.0
            # 7182.0
            # 7156.0
            # 2067.0
            # 2090.0
            # 7187.0
            # 2091.0
            # 2039.0
            if 'up_frequency' in self.ship.keys() and self.ship['up_frequency'] is not None:
                self.frequency = self.ship['up_frequency'] / 1000
            else: 
                self.frequency = 4
        else:
            self.power = 1000
            self.frequency = 5
            
        print(self.ship['name'])
        print(self.power)
        print(self.frequency)


        # send 10 beams or something idk
        # this could be datarate
        # power 
        intensity = self.logmap(self.power,1,100000,20,255)
        color = (intensity, intensity, intensity)
        off = (0,0,0)
        delay = self.logmap(self.rtlt,1,200000,1,10)
        spacing = 11 - self.logmap(self.frequency,1,10,1,10)

        lset = []
        for i in range(0,10):
            lset.append(color)
            if i != 9:
                for i in range(0,spacing):
                    lset.append(off)
        
        print(lset)
        self.lset = lset
        self.progress = 0

    def run(self):
        # slide the lset across the thing
        # in the direction
        if self.groundfirst:
            d = 1
        else:
            d = -1
        
        if self.dir != 'up':
            d = d * -1
        
        # in a groundfirst up, the indexes increase
        # position of first light = d*progress
        # position of second light = d*progress - (d*1)
        # position of third light = d*progress - (d*2)
        for i in range(self.lRange[0],self.lRange[1]):
            #self.lights[]
            pass


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

    
    