#!/bin/bash
#
# Use adb shell commands to set a bandlock configuration on Samsung devices
#
#  Usage:  set an array variable named OPTIONS=( 1 2 E )  and call this script.
#

NAVMENU=(
    MOVE_HOME
    DPAD_UP
    ENTER
    TAB
    TAB
    TAB
    ENTER # Select
)

NAVMENUBACK=(
    MOVE_HOME
    DPAD_UP
    ENTER
    TAB
    ENTER # Back
)

NAVOK=(
    TAB
    TAB
    ENTER
)

SELECTMENU () {
    for KEY in $@; do
        adb shell input keyevent $KEY
    done
}

SELECT () {
    SELECTMENU ${NAVMENU[@]}
    echo "Select option $1"
    adb shell input text $1
    sleep 0.5
    SELECTMENU ${NAVOK[@]}
}

# Return home
adb shell input keyevent HOME
sleep 0.5

# Bring up Samsung engineering mode
adb shell service call phone 1 s16 "*#2263#"
sleep 0.5

for OPTION in ${OPTIONS[@]} ; do
    SELECT $OPTION
done

SELECTMENU ${NAVMENUBACK[@]}

if [ -v DEBUG ]; then
    sleep 2   # IDKHOW this takes so long

    adb shell screencap /sdcard/Pictures/screenshot.png
    adb pull /sdcard/Pictures/screenshot.png

    mkdir -p screenshots
    DATETIME=`date +'%Y-%m-%d_%H:%M:%S'`
    mv screenshot.png screenshots/screenshot_${DATETIME}.png

    echo "open screenshots/screenshot_${DATETIME}.png"

    adb shell dumpsys telephony.registry | grep mServiceState > telephony.registry
    cp telephony.registry screenshots/telephony.registry_${DATETIME}.txt
fi
