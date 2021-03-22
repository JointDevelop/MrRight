#!/bin/bash

echo '** MrRight Server is starting...'

BASE_DIR="/opt/MrRight"

cd $BASE_DIR

echo '**** Virtual enviroment is activating...'
source .venv/bin/activate
echo '**** Virtual enviroment has activated successfully...'

echo '**** Gunicorn is starting...'
gunicorn -c MrRight/gunicorn_config.py MrRight.wsgi
echo '**** Gunicorn has started successfully...'

echo '** MrRight Server start successfully...'

cd -