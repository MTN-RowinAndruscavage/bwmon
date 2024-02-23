#!/bin/bash
#
# Restore band lock to default on Prod Samsung S23+Ultra
#

OPTIONS=(
    1 # Select BAND SELECTION SIM 1
    8 # Select all bands
    9 # Apply band configuration
)

# Uncomment to archive a screenshot of the configuration
DEBUG="True"

source bandlocker.sh

