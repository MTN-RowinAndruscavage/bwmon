#!/bin/bash

if [[ "$1" == "-D" ]]; then

  pushd ${HOME}/bwmon/notify
  pipenv run python3 speedtest_2_msteams.py &

elif [[ "$1" == "-Q" ]]; then
  # kill python speedtest process
  echo "Killing $(ps ax | grep [s]peedtest_2_msteams.py)"
  kill $(ps afx | grep [s]peedtest_2_msteams.py | awk '{print $1}')
fi
