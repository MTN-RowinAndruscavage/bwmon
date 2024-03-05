#!/bin/bash
#
# Set band lock to 5GNSA n258 on Prod Samsung S23+Ultra
#

OPTIONS=(
    1 # Select BAND SELECTION SIM 1
    7 # Clear all bands
    6 # NR5G Band preference
    E # Next page
    8 # NR B258 NSA
    B # GO MAIN
    5 # LTE Band preference
    E # Next page
    C # LTE B66
    E # GO MAIN
    9 # Apply band configuration
)

# Uncomment to archive a screenshot of the configuration
DEBUG="True"

source bandlocker.sh

