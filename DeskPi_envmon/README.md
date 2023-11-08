# DeskPi PicoMate Code

Environmental monitor sensors for the Pico W in the DeskPi PicoMate harness
https://deskpi.com/collections/deskpi-picomate

![DeskPi PicoMate](https://github.com/MTN-RowinAndruscavage/bwmon/assets/8740187/887477a3-32ae-432a-8a20-9ee0df23287e)


This will serve the status of the temperature / humidity sensor, ambient audio levels from the microphone, and motion sensor via HTTP or MQTT
Also displays readings on the OLED panel.

Due to memory constraints, it will only load either the HTTP or MQTT module.

## Installation
This was tested with CircuitPython 8.2.6 .  After flashing CircuitPython, copy all the .py and the settings.toml to the Pico W storage.

Create a lib/ directory and copy the following files and directories into it from the CircuitPython library bundle
https://circuitpython.org/libraries

    adafruit_framebuf.mpy
    adafruit_httpserver
    adafruit_minimqtt
    adafruit_register
    adafruit_requests.mpy
    adafruit_sht31d.mpy
    adafruit_ssd1306.mpy
    neopixel.mpy

Also drop in the font5x8.bin from:
https://github.com/adafruit/Adafruit_CircuitPython_framebuf/blob/main/examples/font5x8.bin

    font5x8.bin

## Configuration

Edit the settings.toml with your wifi credentials.

If you enable MQTT, HTTP will be disabled.  If you need to connect to an unencrypted mqtt server, you will also need to edit the net_mqtt.py code to remove the ssl lines:

        # Delete the following lines to connect to an unsecured MQTT server
        is_ssl=True,
        ssl_context=ssl.create_default_context(),

## Reset button

It's optional but recommended to wire up a button between pins 30 (RST) and 38 (GND) so you don't have to yank the power to reboot this.

The PicoMate button on top left will trigger a graceful shutdown which disconnects from MQTT / HTTP sessions, but is otherwise quite useless.

# Future work

* Set up motion sensor to report movements detected per minute, so the monitor doesn't have to catch the movement at the right moment.

* Set up alert thresholds

* Output directly in CheckMK host format so it doesn't need a companion plugin to run on a separate host

* Add accelerometer & magnetometer monitoring so we can detect earthquakes and EMP events in our data centers

* Do something with the dial button, like changing the font or adjusting alert thresholds.

# Sources

This was pieced together from several other projects and samples:

Sensor readings for DeskPi PicoMate from
https://deskpi.com/blogs/learn/deskpi-picomate-user-manual-and-sources

Network server from
https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server

Ported from micropython to adafruit circuitpython
From https://github.com/Braiuz/RaspberryPiPico_WeatherStation/tree/main

