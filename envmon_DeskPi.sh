#!/bin/bash

# Output readings from Pico W DeskPi PicoMate sensors in the check_mk local format:
# 0 temperature=70.0;60;80;32;110|humidity=48.5;30;70;0;100|motion=1;;;;|microphone=80;1000;2000;0; OK - Temp 70.0 F Humidity 48.5 %

# Customize and install this script in /usr/lib/check_mk_agent/plugins/  on one host monitored by check_mk
# The environmental sensors will appear as a custom check on that host

# Can create multiple copies of this script with different settings for each sensor
CHECKNAME="Env Sensor 1"
SENSORIP="192.168.0.3"

DATA=$(curl -sm 2 http://${SENSORIP}/get) || SUMMARY="CRIT - Failed to connect to sensor $SENSORIP"

# Empty response - Pico W likely dropped to WebREPL mode
echo $DATA | grep '{' > /dev/null || SUMMARY="CRIT - No data returned from sensor"

# Failed message
if [[ "${SUMMARY::2}" == "CR" ]]; then
    CMKSTRING="2 \"${CHECKNAME}\"
temperature=0;20;35;0;50\
|humidity=0;30;70;0;100\
|microphone=0;1000;2000;0;\
 ${SUMMARY}"

# TODO: WARN and CRIT when thresholds are exceeded

else
    # Parse and output metrics for checkmk
    TEMPERATURE=$(echo $DATA | jq ".temperature")
    HUMIDITY=$(echo $DATA | jq ".humidity")
    # MOTION=$(echo $DATA | jq ".motion")
    MICROPHONE=$(echo $DATA | jq ".microphone")

    SUMMARY="OK - Temp ${TEMPERATURE} C, Humidity ${HUMIDITY} %"

    CMKSTRING="0 \"${CHECKNAME}\"
temperature=${TEMPERATURE};20;35;0;50\
|humidity=${HUMIDITY};30;70;0;100\
|microphone=${MICROPHONE};1000;2000;0;\
 ${SUMMARY}"

fi

echo $CMKSTRING
