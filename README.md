# bwmon
Checks and utilities to monitor hourly speedtest-cli and per minute ICMP internet connectivity using CheckMK
https://checkmk.com/


![CheckMK Dashboard Screenshot](https://github.com/MTN-RowinAndruscavage/bwmon/assets/8740187/da9e3b7d-7f73-426c-bdc5-c68a50fc5c04)


This is tested and intended to run on Ubuntu 20.04 systems, but should work on others.

There are several parts:

## Ookla Speedtest plugin for Check_mk
This CheckMK plugin runs speedtest-cli hourly and reports cached entries to the CheckMK server.
Originally from https://github.com/deexno/CheckMK_DSL_check and lightly modified to handle some failure modes.

## Ping DNS
This CheckMK plugin runs the check_icmp nagios plugin to ping the Google 8.8.8.8 GeoIP a few times and reformats the output for CheckMK.  This custom plugin is necessary because the default ping plugin tests from the CheckMK server to the destination IP.  For whatever reason there isn't a simple plugin that tests pings from the monitored host's check_mk_agent to the ping destination IP.

## Slack notification scripts
The notify directory contains two python services that can notify a slack with the results of the hourly speedtests.
There is also a python service and checkmk plugin for environmental monitoring from a DeskPi PicoMate sensor.

# Installation instructions
Check out the install.sh for most of the host agent software dependencies.  This was tested with Check_mk_agent 2.2.

The server-side check plugins in cmk_server/ will need to go somewhere in your /opt/omd/sites/.../lib/check_mk/base/plugins/agent_based/  directory on the CheckMK server.
