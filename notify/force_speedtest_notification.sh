#!/bin/bash

NAGIOS_CMDFILE="/omd/sites/te5ghub/tmp/run/nagios.cmd"
now=`date +%s`

# Force Speedtest notification
/bin/echo "[$now] SEND_CUSTOM_SVC_NOTIFICATION;techexops@localhost;te5ghub;Ookla DSL check;OK;msteams;Test message" >> $NAGIOS_CMDFILE

