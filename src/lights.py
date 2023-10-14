# lights.py
# Written by Starmaid in early 2022

# Builtin Libraries
import asyncio
from platform import libc_ver
import random
import logging
import math as m
import requests
from datetime import datetime, timedelta, timezone
import json
import queue

# External
from PIL import Image

# Set library logging levels
logging.getLogger("PIL").setLevel(logging.WARNING)

# Setup 
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
        """From a loaded image, get a row of pixels.
        Does the down/up sampling"""
        width,height = image.size
        isvalid = row*width < width*height
        if not isvalid:
            return False
        rpix = list(image.getdata())[(width*row):(width*(row+1))]
        rout = [rpix[self.linmap(n,0,numPixels,0,width)][0:3] for n in range(0,numPixels)]
        return rout

    def linmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows.
        This is not great for getting mean pixels. 
        think about it"""
        y = (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
        
        if y < outMin:
            y = outMin
        if y > outMax:
            y = outMax
        return int(y)

    def logmap(self, x, inMin, inMax, outMin, outMax):
        """This is the map() function from Arduino. 
        Im using it to sample from the image rows."""
        try:
            x = m.log10(x)
        except:
            #logging.warning('math exception ' + str(x))
            x = 1
        inMin = m.log10(inMin)
        inMax = m.log10(inMax)

        y = (x - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
        
        if y < outMin:
            y = outMin
        if y > outMax:
            y = outMax
        return int(y)
    
    def noisepx(self, px, rx):
        """apply addative RGB color noise 
        to a single pixel up to radius rx"""
        
        # determine our radius
        r = rx * random.random()

        # determine our direction
        s = [random.gauss(0, 1),random.gauss(0, 1),random.gauss(0, 1)]
        norm = m.sqrt(sum([i*i for i in s]))
        if norm == 0:
            norm = 0.001
        d = [i/norm for i in s]

        # multiply
        vec = [r * i for i in d]

        # add noise change
        newpx = [list(px)[i] + vec[i] for i in range(0,len(px))]

        # ints capped between 0-255
        for i in range(0,len(newpx)):
            newpx[i] = int(newpx[i])
            if newpx[i] < 0:
                newpx[i] = 0
            elif newpx[i] > 255:
                newpx[i] = 255
        
        return tuple(newpx)
    
    def mixpx(self,px1,px2,percent):
        """linear pixel mix between two colors
        starts at px1 and goes to px2 at 100 percent
        also percent should be between 0 and 1"""
        mix1 = [int((1-percent)*i) for i in px1]
        mix2 = [int(percent*i) for i in px2]
        mixresult = tuple([mix1[i]+mix2[i] for i in range(0,len(mix1))])
        return mixresult

    def playImg(self):
        """Play an image row by row on the lights."""
        rout = self.getRow(self.im, self.progress, self.lRange[1]-self.lRange[0])
        if not rout:
            return False
        else:
            self.lights[self.lRange[0]:self.lRange[1]] = rout
            self.progress += 1
        return True

    def run(self):
        """Run should return true until the animation is done playing"""
        return True


class Stop():
    """An empty object that always returns False
    for the run method."""
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
        """Fill section of the lights array with OFF (0,0,0)"""
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,0,0) for i in range(self.lRange[0],self.lRange[1])]
            self.progress = 1
        return True


class Error(LightSequence):
    def __init__(self, lights, lRange, ship=None):
        super().__init__(lights, lRange, ship)

    def run(self):
        """Fill section of the lights array with RED (0,100,0) GRB"""
        if self.progress == 0:
            self.lights[self.lRange[0]:self.lRange[1]] = [(0,100,0) for i in range(self.lRange[0],self.lRange[1])]
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

        # round trip light time (s)
        # from 0 to 200000 (leo to voyager) with -1.0 as None
        # probably do some log scaling
        if self.ship['rtlt'] == -1:
            self.rtlt = 10
        else:
            self.rtlt = self.ship['rtlt']


        if self.dir in ['down', 'both']:
            # Power reported in dBm
            if self.ship['down_power'] == 0:
                self.power = 1
            else:
                self.power = 10 ** ((self.ship['down_power'] - 30) / 10) / 1000
                # Now its gunna be super small so...
                self.power = self.power * 1e22
                if self.power < 1:
                    self.power = 1
            
            # Frequency in MHz
            if 'down_frequency' in self.ship.keys() and self.ship['down_frequency'] is not None:
                self.frequency = self.ship['down_frequency'] / 1000000000
            else:
                self.frequency = 8

        elif self.dir == 'up':
            # Power in kW
            if self.ship['up_power'] is None or self.ship['up_power'] == 0:
                self.power = 0.2 * 1000
            else:
                self.power = self.ship['up_power'] * 1000
            
            # Frequency in GHz
            if 'up_frequency' in self.ship.keys() and self.ship['up_frequency'] is not None:
                self.frequency = self.ship['up_frequency'] / 1000
            else: 
                self.frequency = 4
        else:
            self.power = 1000
            self.frequency = 5

        # Debug a signal
        logging.debug('Dir: ' + str(self.dir))
        logging.debug('Name: ' + str(self.ship['name']))
        logging.debug('Power: ' + str(self.power))
        logging.debug('Freqz: ' + str(self.frequency))

        # Turn the values into lights
        off = (0,0,0)
        intensity = self.logmap(self.power,1,100000,20,255)
        color = (intensity, intensity, intensity)
        self.delay = self.logmap(self.rtlt,1,200000,1,10)
        spacing = 11 - self.logmap(self.frequency,1,10,1,10)

        lset = []
        for i in range(0,10):
            lset.append(color)
            if i != 9:
                for i in range(0,spacing):
                    lset.append(off)
        
        logging.info(lset)
        self.lset = lset
        self.progress = 0

    def run(self):
        # slide the lset across the thing
        # in the direction

        if self.progress % self.delay != 0:
            self.progress += 1
            return True
        
        progadj = int(self.progress / self.delay)

        if self.groundfirst:
            d = 1
        else:
            d = -1
        
        if self.dir != 'up':
            d = d * -1
        
        apos = {}
        for i in range(0,len(self.lset)):
            # for every item in the pattern, hash the color at the location it will display.
            apos[self.lRange[0 if d < 0 else 1] - d*progadj + d*i] = self.lset[i]

        done = True
        for i in range(self.lRange[0],self.lRange[1]):
            # calculate which light position should play
            # if none, then off
            if i in apos.keys():
                done = False
                self.lights[i] = apos[i]
            else:
                self.lights[i] = (0,0,0)

        if done:
            return False
        else:
            self.progress += 1
            return True


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

    def __init__(self, lights, lRange, lat, lng):
        super().__init__(lights, lRange)
        self.green = (0,255,0)
        self.blue  = (30,130,190)
        self.teal  = (10,160,190)
        self.orange= (245,140,0)
        self.night = (5,0,20)
        self.white = (255,255,255)

        self.lat = lat
        self.lng = lng

        self.sunrise = None
        self.sunset  = None
        # set lat long

        # set radius to apply effects
        self.radius = timedelta(hours=1)

        self.delay = 10

        # set list 
        l = self.lRange[1]-self.lRange[0]
        if l > 1:
            self.q = queue.Queue(l)
        else:
            self.q = None
        return
    
    def updateDay(self,offset=0):
        """Pull down new sunrise and sunset times"""
        # some defaults to stop it from crashing...
        self.sunrise = datetime.now().replace(hour=7)
        self.sunset = datetime.now().replace(hour=19)

        # use LOCAL day to ask the api
        endpoint = 'https://api.sunrise-sunset.org/json'
        data = {
            'lat': self.lat,
            'lng': self.lng,
            'date':datetime.now().strftime("%Y-%m-%d"),
            'formatted':0
        }

        try:
            r = requests.get(endpoint,params=data,verify=False)
        except requests.exceptions.ConnectionError as e:
            logging.error("Unable to reach api.sunrise-sunset.org")
            return
        except requests.exceptions.RequestException as e:
            logging.error(f"Other requests error:\n {e}")
            return
        
        sundata = json.loads(r.content.decode('UTF-8'))

        # parse as some simple representation
        # convert from UTC to current time
        #sunrise = datetime.fromisoformat(sundata['results']['sunrise'])

        # get the things
        self.sunrise = datetime.fromisoformat(sundata['results']['civil_twilight_begin'])
        self.sunset  = datetime.fromisoformat(sundata['results']['civil_twilight_end'])
    
    def run(self):
        # check if we even have a ground to update
        if self.q is None:
            return True

        if self.progress % self.delay != 0:
            self.progress += 1
            return True
        else:
            self.progress = 0
        
        # what daytime is it
        self.now = datetime.now(timezone.utc)

        # do we have data for today?
        # if no, get the next events
        # if yes, continue
        if self.sunrise is None or self.now - self.sunrise > timedelta(hours=20):
            # we need to get new ones
            self.updateDay()
        
        if self.sunrise - self.now > timedelta(seconds=0):
            #if self.sunrise - self.now > self.sunrise:
            # night
            newpx = self.night
        elif self.sunrise - self.now > -self.radius:
            # sunrise - fade through blue
            # find what percentage along the transition we are
            # percent = (self.now - (self.sunrise - self.radius)) / (self.radius)
            percent = (self.now - self.sunrise) / (self.radius)
            mix1result = self.mixpx(self.night, self.blue, percent)

            # pull the color in the direction of teal
            if percent < 0.5:
                newpx = self.mixpx(mix1result,self.teal,percent*2)
            else:
                newpx = self.mixpx(mix1result,self.teal,2-(percent*2))
            
        elif self.sunset - self.now > self.radius:
            # day
            if random.randint(0,10) <= 7:
                newpx = self.blue
            else:
                newpx = self.white

        elif self.sunset - self.now > timedelta(seconds=0):
            #elif self.sunset - self.now > - self.radius:
            # sunset - fade through orange
            #percent = (self.now - (self.sunset - self.radius)) / (self.radius*2)
            percent = (self.now - self.sunset) / (self.radius)
            mix1result = self.mixpx(self.blue, self.night, percent)

            # pull the color in the direction of orange
            if percent < 0.5:
                newpx = self.mixpx(mix1result,self.orange,percent*2)
            else:
                newpx = self.mixpx(mix1result,self.orange,2-(percent*2))
        else:
            # night again
            newpx = self.night

        # apply noise to the pixel to vary it
        newpx = self.noisepx(newpx,20)

        # fifo that pixel into the list
        while not self.q.full():
            self.q.put(newpx)

        self.q.get()
        self.q.put(newpx)

        # render all pixels
        q2 = queue.Queue()
        for p in range(self.lRange[0],self.lRange[1]):
            px = self.q.get()
            self.lights[p] = px
            q2.put(px)
        
        # put them back in the queue
        while not self.q.full():
            i = q2.get()
            self.q.put(i)

        self.progress += 1
        return True

class Img(LightSequence):
    """Class to play an image line by line."""
    
    def __init__(self, lights, lRange, theme, filename, ship=None):
        super().__init__(lights, lRange, ship)
        self.stop = not self.openImg(theme + '/' + filename + '.png')
        
        if self.stop:
            logging.error(f"unable to load {filename} from {theme}")
    
    def run(self):
        return self.playImg()

    
    