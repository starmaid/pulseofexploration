#!/bin/bash

echo
echo "This script will set up all requirements for the Pulse"
echo "Make sure this device is connected to the internet."
echo

# Adafruit pre-circuitpytohn
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install python3-pip
sudo pip3 install --upgrade setuptools

# Adafruit install
cd ~
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
#sudo python3 raspi-blinka.py

# WS2812 install
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

# set config in ./data/config.json easily


# Set up a daemon or autorun
# crontab -e
# echo "@reboot python /home/pi/pulseofexploration/run.sh" >> ?thecrontabfile?