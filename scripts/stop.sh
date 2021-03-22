#!/bin/bash

echo '** MrRight Server is stopping...'

BASE_DIR="/opt/MrRight"
GUNICORN_PID_FILE="$BASE_DIR/logs/gunicorn.pid"

if [ -f $GUNICORN_PID_FILE ]; then
  GUNICORN_PID=`cat $GUNICORN_PID_FILE`
  sudo kill $GUNICORN_PID
  echo "**** Gunicorn(PID:$GUNICORN_PID) is killed."
  echo "** MrRight Server stop successfully..."
else
  echo '** MrRight Server dose not start yet... Please start it firstly...'
fi
