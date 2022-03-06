# Pulse of Exploration (mini)

I love [Dan Goods' art installation at JPL "Pulse of Exploration"](https://vimeo.com/93420747)

I love [cool light displays](https://starmaid.github.io/projects/hallie-lights)

This pulls data from [JPL Eyes DSN.](https://eyes.nasa.gov/dsn/dsn.html)

This project uses [Adafruit CircuitPython](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/overview)

WS2812 light strips and [their python library from adafruit](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage)

## Who made these animation themes?

Check out the README files in each theme folder!

## Where are you in development??

make a setup script for the user

make a cool ground, reactive to time of day

## How to Build your Own



## Power Consumption Details

WS2812b strip, draws about 55 mA/px

| Board  | Power Draw (mA) |
| ------ | --------------- |
| Zero W | 300     |
| 3 B+   | 700     |
| 4 B    | 800     |

With a 2 A power supply that you probably have lying around, you should be able to get MAXIMUM 20 LEDs driven on the larger boards, and 30 on the Zero. Remember, this is with no keyboard or display, which would increase draw. This forces you to setup and control it over SSH, which is easy.