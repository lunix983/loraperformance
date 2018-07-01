#!/bin/bash

FILENAME="iotnetworkserver.py"
cd '/home/iotadmin/git/loraperformance/webservice/'
sed -i 's/\/Users\/Luix\/PycharmProjects\/iotelasticproject/\/var\/log\/iotnetworkserver/' "$FILENAME"
sed -i 's/\#\ //' "$FILENAME"
cp -a $FILENAME '/opt/iotnetworkserver'
