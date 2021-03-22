#!/bin/bash

BASE_DIR="/opt/MrRight"

cd $BASE_DIR

source .venv/bin/activate
nohup celery worker -A tasks --loglevel=INFO > logs/celery.log 2>&1 &

cd -