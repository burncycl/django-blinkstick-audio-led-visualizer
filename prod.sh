#!/bin/bash

# This will start bsvapp in Production mode (i.e. with uwsgi support for Nginx).

# Switch to project directory and start uwsgi server.
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${DIR}/bsv

uwsgi \
--socket :8001 \
--module bsv.wsgi \
--chmod-socket=664 \
--master \
--enable-threads \
--processes=5 \
--threads=5 \
--harakiri=20 \
--max-requests=5000 \
--close-on-exec \
--enable-threads \
--workers=1 \
--vacuum

#--close-on-exec \
#--enable-threads \
#--workers=1 \

