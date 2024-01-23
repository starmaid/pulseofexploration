# dsn.py
# written by Starmaid in early 2022

# Builtin Libraries
import xml.etree.ElementTree as ET
import requests
from datetime import datetime
import logging

# Set library logging levels
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
        """Ask DSN Now whats up and return the data"""
        signals = {}

        try:
            dishxml = requests.get('https://eyes.nasa.gov/dsn/data/dsn.xml')
        except requests.exceptions.ConnectionError as e:
            logging.error("Unable to reach eyes.nasa.gov.")
            return signals
        except requests.exceptions.RequestException as e:
            logging.error(f"Other requests error:\n {e}")
            return signals
            

        # Get the actual xml object to work with
        comms = ET.fromstring(dishxml.text)

        # Go through each dish
        # find all down and upsignals
        # add each found spaceship and power/frequency to a list
        # translate shortnames to friendlynames
        

        for dish in comms.findall('./dish'):
            for target in dish.findall('./target'):
                # These are the spacecraft
                sDict = {}
                name = target.attrib['name'].lower()
                if name == "":
                    continue
                
                sDict['name'] = name
                try:
                    sDict['friendlyName'] = self.friendlyTranslator[name]
                except:
                    # No clue why this would happen but eh lets be safe
                    #logging.debug("key " + name + " not found")
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
                                sDict['up_frequency'] = float(signal.attrib['frequency'])
                            except ValueError:
                                sDict['up_frequency'] = None

                            try:
                                sDict['up_band'] = signal.attrib['band']
                            except:
                                sDict['up_band'] = None
                            
                if 'up' not in sDict.keys():
                    sDict['up'] = False
                    sDict['up_power'] = None
                    sDict['up_dataRate'] = None
                    sDict['up_frequency'] = None
                    sDict['up_band'] = None
                
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
                        
                            try:
                                sDict['down_band'] = signal.attrib['band']
                            except:
                                sDict['down_band'] = None

                if 'down' not in sDict.keys():
                    sDict['down'] = False
                    sDict['down_power'] = None
                    sDict['down_dataRate'] = None
                    sDict['down_frequency'] = None
                    sDict['down_band'] = None
                
                if (not sDict['down']) and (not sDict['up']):
                    continue
                
                sDict['range'] = float(target.attrib['uplegRange']) # in km
                sDict['rtlt'] = float(target.attrib['rtlt']) # in seconds
                sDict['dish'] = dish.attrib['name']
                

                # add logic to ignore signals that arent ready
                # a signal needs to have rtlt, power, band||frequnency
                if sDict['up']:
                    ds = 'up_'
                else:
                    ds = 'down_'

                if (sDict['rtlt'] 
                    and sDict[f'{ds}power']
                    and (sDict[f'{ds}frequency'] or sDict[f'{ds}band'])):
                    signals[name] = sDict
                    #logging.debug(f"signal {name} has all valid fields.")
                else:
                    logging.debug(f"signal {name} not ready.")
        
        # Remove things we dont care about
        # Mind control voice: KILL TESTING
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
        """Look at the data returned from DSN and
        determine which signals are new"""
        signals = self.poll()
        
        newsignals = {}
        
        # Add any new signal we just saw to the active ones
        for s in signals.keys():
            if s not in self.activeSignals.keys():
                # if the key isnt found, add to both lists.
                newsignals[s] = signals[s]
                self.activeSignals[s] = signals[s]
            else:
                # if the key is there, the signal info may have changed
                # hopefully this will play downlink signals now :)
                if ((signals[s]['up'] != self.activeSignals[s]['up'])
                    or (signals[s]['down'] != self.activeSignals[s]['down'])):
                    newsignals[s] = signals[s]
                    self.activeSignals[s] = signals[s]
        
        # Remove signal if it is no longer active
        removenames = []
        for s in self.activeSignals.keys():
            if s not in signals.keys():
                removenames.append(s)
        
        for name in removenames:
            self.activeSignals.pop(name)

        if len(newsignals) > 0:
            logging.debug('\n' + str(newsignals))
        
        return newsignals
