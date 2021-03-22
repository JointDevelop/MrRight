#!/bin/bash

BASE_DIR="/opt/MrRight"

cd $BASE_DIR

source .venv/bin/activate
nohup celery -A asyntasks worker --loglevel=INFO > logs/celery.log 2>&1 &

cd -