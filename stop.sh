#!/bin/bash

# Stop script, works in conjunction with systemd /etc/systemd/system/blinkstickviz.service

./kill_workers.sh
/usr/bin/pkill pulseaudio.sh
/usr/bin/pkill pulseaudio
/usr/local/bin/uwsgi --stop /home/pi/bsv.pid
pkill uwsgi
ps auxww | grep 'uwsgi' | awk '{print $2}' | xargs kill -9 2&> /dev/null
ps auxww | grep 'uwsgi' | awk '{print $2}' | xargs kill -9 2&> /dev/null
redis-cli FLUSHALL 
