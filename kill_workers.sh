#!/bin/bash

# Script designed to work with Celery 5.0.0

APP="bsv"
cd ./${APP}
celery -A ${APP} purge -f
# Kill off previous running workers (if any).
ps auxww | grep 'celery -A' | awk '{print $2}' | xargs kill 2&> /dev/null
ps auxww | grep 'celery -A' | awk '{print $2}' | xargs kill -9 2&> /dev/null


