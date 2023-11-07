# bwmon
Checks and utilities to monitor hourly speedtest-cli and per minute ICMP internet connectivity using CheckMK
https://checkmk.com/

This is tested and intended to run on Ubuntu 20.04 systems, but should work on others.

There are several parts:

## Ookla Speedtest plugin for Check_mk
This CheckMK plugin runs speedtest-cli hourly and reports cached entries to the CheckMK server.

## Ping DNS
This CheckMK plugin runs the check_icmp nagios plugin to ping the Google 8.8.8.8 GeoIP a few times and reformats the output for CheckMK.  This custom plugin is necessary because the default ping plugin tests from the CheckMK server to the destination IP.  For whatever reason there isn't a simple plugin that tests pings from the monitored host's check_mk_agent to the ping destination IP.

## Slack notification scripts
The notify directory contains two python services that can notify a slack with the results of the hourly speedtests.
There is also a python service and checkmk plugin for environmental monitoring from a DeskPi PicoMate sensor.
