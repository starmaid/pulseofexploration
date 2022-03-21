import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger('charset_normalizer').setLevel(logging.WARNING)

class DSNQuery:
    """Handles data queries from NASA DSN"""

    def __init__(self):
        self.activeSignals = {}
        self.getFriendlyNames()


    def getFriendlyNames(self):
        # get friendly names
        friendlyxml = requests.get('https://eyes.nasa.gov/dsn/config.xml')
        parser = ET.XMLParser(encoding='UTF-8')
        friendlynames = ET.fromstring(friendlyxml.text, parser=parser)
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

        for dish in comms.findall('./dish'):
            for target in dish.findall('./target'):
                sDict = {}
                name = target.attrib['name'].lower()
                if name == "":
                    continue

                sDict['name'] = name
                try:
                    sDict['friendlyName'] = self.friendlyTranslator[name]
                except:
                    #print("key " + name + " not found")
                    continue

                for signal in dish.findall('./upSignal'):
                    if signal.attrib['signalType'] != 'none':
                        if signal.attrib['spacecraft'].lower() == name:
                            sDict['up'] = True
                            try:
                                sDict['up_power'] = float(signal.attrib['power'])
                            except ValueError:
                                sDict['up_power'] = None
                            
                            try:
                                sDict['up_dataRate'] = float(signal.attrib['dataRate'])
                            except ValueError:
                                sDict['up_dataRate'] = None
                            
                            try:
                                sDict['up_'] = float(signal.attrib['frequency'])
                            except ValueError:
                                sDict['up_frequency'] = None
                            
                if 'up' not in sDict.keys():
                    sDict['up'] = False
                    sDict['up_power'] = None
                    sDict['up_dataRate'] = None
                    sDict['up_frequency'] = None
                
                for signal in dish.findall('./downSignal'):
                    if signal.attrib['signalType'] != 'none':
                        if signal.attrib['spacecraft'].lower() == name:
                            sDict['down'] = True
                            try:
                                sDict['down_power'] = float(signal.attrib['power'])
                            except ValueError:
                                sDict['down_power'] = None
                            
                            try:
                                sDict['down_dataRate'] = float(signal.attrib['dataRate'])
                            except ValueError:
                                sDict['down_dataRate'] = None
                            
                            try:
                                sDict['down_frequency'] = float(signal.attrib['frequency'])
                            except ValueError:
                                sDict['down_frequency'] = None
                        
                if 'down' not in sDict.keys():
                    sDict['down'] = False
                    sDict['down_power'] = None
                    sDict['down_dataRate'] = None
                    sDict['down_frequency'] = None
                
                if (not sDict['down']) and (not sDict['up']):
                    continue

                sDict['range'] = float(target.attrib['uplegRange']) # in km
                sDict['rtlt'] = float(target.attrib['rtlt']) # in seconds
                sDict['dish'] = dish.attrib['name']
                signals[name] = sDict
        
        # remove things we dont care about
        for i in ["dsn", "dss", "test", "testing", "Testing"]:
            try:
                signals.pop(i)
            except:
                pass
        
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

