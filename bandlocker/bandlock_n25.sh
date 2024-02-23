#!/bin/bash
#
# Set band lock to 5GSA n25 on Prod Samsung S23+Ultra
#

OPTIONS=(
    1 # Select BAND SELECTION SIM 1
    7 # Clear all bands
    6 # NR5G Band preference
    A # NR B25 SA
    F # GO MAIN
    9 # Apply band configuration
)

# Uncomment to archive a screenshot of the configuration
DEBUG="True"

source bandlocker.sh

