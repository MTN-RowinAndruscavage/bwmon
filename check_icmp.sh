#!/bin/bash

# Parse output of monitoring-plugins check_icmp in the format:
# OK - 8.8.8.8: rta 25.134ms, lost 0%|rta=25.134ms;200.000;500.000;0; pl=0%;40;80;; rtmax=40.309ms;;;; rtmin=19.837ms;;;; 

# And convert to the Check_MK local check format, converting milliseconds to seconds
# 0 "Ping DNS" rta=0.025134;0.200;0.500;0;|pl=0;40;80;;|rtmax=0.040309;;;;|rtmin=0.019837;;;; OK - 8.8.8.8: rta 25.134ms, lost 0%

CHECKICMP=$(/usr/lib/nagios/plugins/check_icmp 1.1.1.1)

IFS='|' read -ra ADDR <<< "$CHECKICMP"
SUMMARY=${ADDR[0]}

## Quick and dirty way, but unfortunately we should convert milliseconds to seconds for CheckMK
# IFS=' ' read -ra DATA <<< "${ADDR[1]}"
# echo "0 \"Ping DNS\" ${DATA[0]::-2};200;500;0;|${DATA[4]:1:-1};40;80;; ${ADDR[0]}"


# Parse all the things so we can do a little math
if [[ "${SUMMARY::2}" == "OK" ]]; then
    IFS=' ' read -ra METRIC <<< "${ADDR[1]}"
    CMKSTRING=""
    METRICSEP=""
    for F in "${METRIC[@]}"; do
	IFS='=' read -ra DATA <<< "${F}"
	FIELD=${DATA[0]}
	VALUES=${DATA[1]}

	# Expect 5 values: Value;WARN;CRIT;LOW;HIGH
	NUM=("","","","","")
	IFS=';' read -ra NS <<< "${VALUES}"
	# declare -p NS

	# If value ends in ms, strip unit and convert all five values from ms to seconds
	SCALE=1
	if [[ ${NS[0]: -2} == "ms" ]]; then
	    SCALE=0.001
	    # echo "Set scaling to $SCALE"
	fi
	for ((i=0;i<5;i++)); do
	    # Strip units and other non-numeric characters from numbers
	    NSF=${NS[i]//[!0-9.]/}
	    if [[ ! -z "$NSF" ]]; then
		# echo "scale=4;$NSF*$SCALE"
		NUM[$i]=$(echo "scale=4;$NSF*$SCALE" |bc)
	    else
		NUM[$i]=$NSF
	    fi
	done

	FIXEDVALUES=""
	SEP=""
	for N in "${NUM[@]}"; do
	    FIXEDVALUES="${FIXEDVALUES}${SEP}${N}"
	    SEP=";"
	done
	    
	CMKSTRING="${CMKSTRING}${METRICSEP}${FIELD}=${FIXEDVALUES}"
	METRICSEP="|"
	
    done
    
    echo "0 \"Ping DNS\" ${CMKSTRING} ${SUMMARY}"

else
    echo "2 \"Ping DNS\" rta=0.0;0.200;0.500;0;|pl=100;40;80;;|rtmax=0;;;;|rtmin=0;;;; ${SUMMARY}"

fi
