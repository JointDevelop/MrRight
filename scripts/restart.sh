#!/bin/bash

echo '** MrRight Server is restarting...'

BASE_DIR="/opt/MrRight"
GUNICORN_PID_FILE="$BASE_DIR/logs/gunicorn.pid"

if [ -f $GUNICORN_PID_FILE ]; then
  GUNICORN_PID=`cat $GUNICORN_PID_FILE`
  sudo kill -HUP $GUNICORN_PID
  echo "**** Gunicorn(Master PID:$GUNICORN_PID): "
  echo "******** New Worker processes is created. "
  echo "******** Current worker processes will be killed smoothly."
  echo "** MrRight Server restart successfully..."
else
  echo '** MrRight Server dose not start yet. Let it start now...'
  $BASE_DIR/scripts/start.sh
fi



