#!/bin/bash

echo
echo "This script will update the software to the latest version"
echo

# Save some variables
RUNDIR=`pwd`
DATE=`date +%s`
CFILED="../config"$DATE".json"
CFILEDN="./data/config"$DATE".json"
CFILE="./data/config.json"

# Copy the current config file
cp $CFILE $CFILED

# Reset and pull changes
git reset --hard HEAD
git pull 

# Copy the new clean config to a .clean file
cp $CFILE $CFILE".clean"

# Move the old config file back into place
cp $CFILED $CFILE
mv -f $CFILED $CFILEDN

# Make sure run is executable
chmod +x ./run.sh
chmod +x ./update.sh

echo
echo "Old config file saved as "$CFILEDN
echo "If you have issues, look at "$CFILE".clean for new config format"
echo