# Pulse of Exploration (mini)

I love [Dan Goods' art installation at JPL "Pulse of Exploration"](https://vimeo.com/93420747)

This pulls data from [JPL Eyes DSN.](https://eyes.nasa.gov/dsn/dsn.html)

This project uses [Adafruit CircuitPython](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/overview)

WS2812 light strips and [their python library from adafruit](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage)


## Where are you in development??

You are implementing the Lights.LightSequence.getRow() function. Currently it is not behaving properly.

it is:
- maybe not sampling right using the vmap function
- injecting random longer tuples
- being generally weird

after that you need to generalize all the planet functions.

## Further Steps

Finish adding all the planets incl. deep and near space

Make a cool transmission animation (maybe draw, but maybe do programatically)

-- check to make sure it works with dsn and with real lights -- 

make a setup script for the user

make a cool ground, reactive to time of day



