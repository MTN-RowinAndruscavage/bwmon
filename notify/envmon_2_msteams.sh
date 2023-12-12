#!/bin/bash

if [[ "$1" == "-D" ]]; then

  pushd ${HOME}/bwmon/notify
  pipenv run python3 envmon_2_msteams.py &

  #  pipenv run python3 envmona_2_slack.py &
  #  pipenv run python3 envmonb_2_slack.py &

elif [[ "$1" == "-Q" ]]; then
  # kill python envmon process
  echo "Killing $(ps ax | grep [e]nvmon_2_msteams.py)"
  kill $(ps afx | grep [e]nvmon_2_msteams.py | awk '{print $1}')
fi
