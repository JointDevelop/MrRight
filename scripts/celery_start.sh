#!/bin/bash

BASE_DIR="/opt/MrRight/"
source $BASE_DIR/.venv/bin/activate
nohup celery worker -A tasks --loglevel=INFO > logs/celery.log 2>&1 &