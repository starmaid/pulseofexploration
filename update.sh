#!/bin/bash

echo
echo "This script will update the software to the latest version"
echo

# Save some variables
RUNDIR=`pwd`
DATE=`date +%s`
CFILED="../config"$DATE".json"
CFILE="./data/config.json"

# Copy the current config file
cp "./data/config"$DATE".json" $CFILED

# Reset and pull changes
git reset --hard HEAD
git pull 

# Copy the new clean config to a .clean file
cp $CFILE $CFILE".clean"

# Move the old config file back into place
mv -f $CFILED $CFILE

# Make sure run is executable
chmod +x ./run.sh

echo
echo "Old config file saved as "$CFILED
echo "If you have issues, look at "$CFILE".clean for new config format"
echo