#!/bin/bash

# Kill off previous running workers (if any).
ps auxww | grep 'celery -A' | awk '{print $2}' | xargs kill 2&> /dev/null
ps auxww | grep 'celery -A' | awk '{print $2}' | xargs kill -9 2&> /dev/null

APP="bsv"

cd ./${APP}

celery -A ${APP} purge -f
celery -A ${APP} worker --loglevel=INFO --pool=prefork --concurrency=1 -n worker1@%h &
celery -A ${APP} worker --loglevel=INFO --pool=prefork --concurrency=1 -n worker2@%h &

#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker1@%h &
#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker2@%h &
#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker3@%h &
#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker4@%h &
#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker5@%h &
#celery worker -A ${APP} -l info --pool=solo --concurrency=1 -n worker6@%h &
