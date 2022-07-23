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
sudo apt install libopenjp2-7 -y
sudo pip3 install requests pillow

# Enable GPIO?

# Make run.sh executable
cd $RUNDIR
chmod +x ./run.sh
chmod +x ./update.sh

# Set up an autorun at boot. No need to eat output, logs go directly to their files
(crontab -l ; echo "@reboot sleep 20 && /home/"$USER"/pulseofexploration/run.sh &") | uniq - | crontab -

# tell user to set timezone
echo "\n\nConfiguration complete."
echo "Your set timezone is:"
cat /etc/timezone
echo "If this is not accurate, enter 'sudo raspi-config' and set your local timezone under localization settings."

echo "\nAlso remember to edit ./data/config.json to finish setting up your lights! \n"