#!/bin/bash


LOCAL="./"
REMOTE="/opt/MrRight"
USER='root'
HOST='124.71.145.179'

rsync -crvP --exclude={.git,.venv,__pycache__,logs} $LOCAL $USER@$HOST:$REMOTE
echo '** Upload code to remote complete...'

read -p "**** Do you want to restart server? (y/n)" restart
if [[ $restart == "y" ]]; then
  echo '**** Begin to restart server...'
  ssh $USER@$HOST "$REMOTE/scripts/restart.sh"
fi





