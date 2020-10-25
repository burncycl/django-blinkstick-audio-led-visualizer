#!/bin/bash

# Starts Django in development node on screen process.

SCRIPT_PATH="$( cd "$(dirname "$0")" ; pwd -P )"
PROCESS_ID=`ps -ef|egrep SCREEN|egrep audit|awk '{print $2}'`
SCREEN=`which screen`

kill -15 $PROCESS_ID
sleep 1
${SCREEN} -dmS bsv bash -c "${SCRIPT_PATH}/start.sh"
