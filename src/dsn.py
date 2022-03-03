from os import remove
import xml.etree.ElementTree as ET
import requests
from datetime import datetime

class DSNQuery:
    """Handles data queries from NASA DSN"""

    def __init__(self):
        self.activeSignals = {}
        self.getFriendlyNames()


    def getFriendlyNames(self):
        # get friendly names
        friendlyxml = requests.get('https://eyes.nasa.gov/dsn/config.xml')
        friendlynames = ET.fromstring(friendlyxml.text)
        # make dict of friendlynames
        allships = friendlynames.findall("./spacecraftMap/spacecraft")
        self.friendlyTranslator = {}

        for ship in allships:
            self.friendlyTranslator[ship.attrib['name']] = ship.attrib['friendlyName']

    
    def poll(self):
        # get whos talking
        dishxml = requests.get('https://eyes.nasa.gov/dsn/data/dsn.xml')
    
        # this gives us the actual xml object to work with
        comms = ET.fromstring(dishxml.text)

        # go through each dish
        # find all down and upsignals
        # add each found spaceship and power/frequency to a list
        # translate shortnames to friendlynames

        signals = {}

        """
        # this part looks at signals between dishes and probes
        # look at this later to see if you want to look at frequency and power
        # for now, its omitted because i dont want to do it.
        for signal in comms.findall("./dish/upSignal") + comms.findall("./dish/downSignal"):
            sDict = {}
            name = signal.attrib['spacecraft']
            if name == "":
                continue
            
            sDict['name'] = name
            sDict['friendlyName'] = self.friendlyTranslator[name.lower()]
            sDict['power'] = signal.attrib['power'] # in dB
            sDict['frequency'] = signal.attrib['frequency'] # in hertz
            signals[name] = sDict
        """

        for target in comms.findall("./dish/target"):
            sDict = {}
            name = target.attrib['name'].lower()
            if name == "":
                continue
            
            sDict['name'] = name
            try:
                sDict['friendlyName'] = self.friendlyTranslator[name]
            except:
                print("key " + name + " not found")
                continue
            
            sDict['range'] = float(target.attrib['uplegRange']) # in km
            sDict['rtlt'] = float(target.attrib['rtlt']) # in seconds
            signals[name] = sDict

        
        #print(signals)
        # remove things we dont care about
        for i in ["dsn", "dss", "test", "testing", "Testing"]:
            try:
                signals.pop(i)
            except:
                pass
        #print(signals)
        
        # do we care about timestamps?
        #ts = int(comms.findall("timestamp")[0].text) / 1000
        #timestring = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        
        return signals

    def getNew(self):
        signals = self.poll()
        
        newsignals = []
        
        # Add any new signal we just saw to the active ones
        for s in signals.keys():
            if s not in self.activeSignals.keys():
                newsignals.append(s)
                self.activeSignals[s] = signals[s]
        
        # Remove signal if it is no longer active
        removenames = []
        for s in self.activeSignals.keys():
            if s not in signals.keys():
                removenames.append(s)
        
        for name in removenames:
            self.activeSignals.pop(name)

        if len(newsignals) > 0:
            print('\n' + str(newsignals))
        
        return newsignals

