#!/bin/bash

echo
echo "This script will set up all requirements for the miniPulse"
echo

RUNDIR=`pwd`

# Adafruit pre-circuitpytohn
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip -y
sudo pip3 install --upgrade setuptools

# Adafruit install
cd ~
sudo pip3 install --upgrade adafruit-python-shell
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
#sudo python3 raspi-blinka.py

# WS2812 install
sudo pip3 install rpi_ws281x adafruit-circuitpython-neopixel
sudo python3 -m pip install --force-reinstall adafruit-blinka

# Install other dependencies
sudo pip3 install requests pillow

# Make run.sh executable
cd $RUNDIR
chmod +x ./run.sh

# Set /dev/mem permissions
sudo adduser pi gpio
sudo chown pi.gpio /dev/mem
sudo chmod a+rw /dev/mem

# Set up an autorun at boot. No need to eat output, logs go directly to their files
(crontab -l ; echo "@reboot /home/pi/pulseofexploration/run.sh") | uniq - | crontab -