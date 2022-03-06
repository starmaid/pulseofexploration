# Pulse of Exploration (mini)

I love [Dan Goods' art installation at JPL "Pulse of Exploration"](https://vimeo.com/93420747)

I love [cool light displays](https://starmaid.github.io/projects/hallie-lights)

This pulls data from [JPL Eyes DSN.](https://eyes.nasa.gov/dsn/dsn.html)

This project uses [Adafruit CircuitPython](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/overview)

WS2812 light strips and [their python library from adafruit](https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage)

## Who made these animation themes?

Check out the README files in each theme folder!

## Where are you in development??

Variable brightness for LEDS

make a setup script for the user

make a cool ground, reactive to time of day

## How to Build your Own

### Parts

| Item   | Avg. Cost |
| ------ |----------|
| Raspberry Pi Zero W |  $10 |
| 4GB or larger microSD card | $8 |
| 2A or more power adapter + cable | $5 |
| WS2812b light strip | $10 |

**NOTE:** There is currently a global shortage of Raspberry Pi devices. It is more likely you will be able to pick one up from a local computer store for MSRP than online.

### Tools

- MicroSD adapter for your computer
- Wire cutters
- Knife

### Steps

1. First, pick a Raspberry Pi. I have some 3B+'s lying around, so that's what I'll be using. Most models will work. If you are purchasing one for this project, I reccomend the Pi Zero W.

2. Download the latest [Raspberry Pi OS Lite](https://www.raspberrypi.com/software/operating-systems/).

3. If you don't already have a software to flash disk images with, download [Etcher](https://www.balena.io/etcher/).

4. If you are using a Windows PC and don't have access or simply dont want to dig into your router's DCHP assignments (or don't know what I just said), download [bonjour services](https://support.apple.com/kb/DL999?locale=en_US).

5. Connect the MicroSD card to your computer. Use Etcher to flash the OS image you just downloaded.

6. Download from this GitHub page [wpa_cupplicant.conf]() and [ssh]()

6. Using a text editor (like notepad), edit the `wpa_supplicant.conf` file to include the credentials for your wifi network.

7. Copy both the `wpa_supplicant.conf` and `ssh` files into the `X:/boot` drive that appears after flashing the SD card.

8. Remove the MicroSD card from your computer and put it in the Raspberry Pi.

9. 



## Power Consumption Details

WS2812b strip, draws about 55 mA/px

| Board  | Power Draw with mild load (mA) | Lights you could power with a 2 A Supply |
| ------ | --------------- | ---------------------- |
| Zero W | 300     | 30 |
| 3 B+   | 700     | 22 |
| 4 B    | 800     | 20 |

Remember, this is with no keyboard or display, which would increase draw. This forces you to setup and control it over SSH, which is easy.

The Zero does not have a 5V regulator that limits how much current you can pull through the traces, which gives you more flexibility.