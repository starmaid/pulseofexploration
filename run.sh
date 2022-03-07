#!/bin/bash

date
echo "Starting the Pulse"

# make sure in the proper directory
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# run the program
sudo python3 ./src/main.py