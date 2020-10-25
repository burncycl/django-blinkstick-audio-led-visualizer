#!/bin/bash

# Starts Django in development mode. Works in conjunction with boot_workers.sh script. 

PROCESS_ID=`ps -ef|egrep python|egrep 8080|awk '{print $2}'| head -n 1`
kill ${PROCESS_ID}

source ./venv/bin/activate
cd bsv
python3 manage.py makemigrations
python3 manage.py makemigrations bsvapp
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:8080

