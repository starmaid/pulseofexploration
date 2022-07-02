#!/bin/bash

CRONFILE="/home/"$USER"/cron_out.txt"

date >> $CRONFILE
echo "Starting the Pulse" >> $CRONFILE

# make sure in the proper directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# run the program
sudo python3 ./src/main.py >> $CRONFILE