# Sensor readings for DeskPi PicoMate from
# https://deskpi.com/blogs/learn/deskpi-picomate-user-manual-and-sources

# Network server from
# https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server

# From https://github.com/Braiuz/RaspberryPiPico_WeatherStation/tree/main
# ported from micropython to adafruit circuitpython

import os, microcontroller, board, busio
import time
import gc
import asyncio

# Can't find this optical sensor driver
# from adafruit_ltr381rgb import LTR381RGB
from mic import *

from sensor_data import *

# There's only enough memory to run HTTP or MQTT
if os.getenv('mqtt_broker'):
    from net_mqtt import *
else:
    from net_httpserver import *

# Optionally run checkmk agent
if os.getenv('CHECKMK_PORT'):
    from net_socket import *

# Sensors and Display need to be loaded after MQTT
# Temperature sensor
from adafruit_sht31d import SHT31D
# OLED
from adafruit_ssd1306 import SSD1306_I2C

import digitalio
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

button = digitalio.DigitalInOut(board.GP26)
button.direction = digitalio.Direction.INPUT
button.pull = digitalio.Pull.UP

pir = digitalio.DigitalInOut(board.GP28)
pir.direction = digitalio.Direction.INPUT
pir.pull = digitalio.Pull.DOWN

def StopApplication():
    print('Interrupted')
    led.value = False

def display_text(display, str, line):
    display.text(str, 0, (line % 8) * 8, 2, font_name="lib/font5x8.bin")
    #display.text(str, 0, (line % 16) * 16, 2, size=2, font_name="lib/font5x8.bin")


def Restart():
    print("restarting...")
    Blink(5)
    display.fill(1)
    display.show()
    net_close()
    time.sleep(0.5)
    display.fill(0)
    display.show()
    microcontroller.reset()

def Sensor_Init():
    i2cl = busio.I2C(scl = board.GP15, sda = board.GP14)
    sensor = SHT31D(i2cl)
    # optical = LTR329(i2cl)
    print("Sensor init done")
    return sensor

def Display_Init():
    i2c0 = busio.I2C(scl = board.GP17, sda = board.GP16)
    display = SSD1306_I2C(128, 64, i2c0)
    print("Display init done")
    return display

async def Sensor_Heat(sensor):
    # Burn off condensation from humidity sensor about every 10 sec
    sensor.heater = True
    print("Sensor Heater status =", sensor.heater)
    time.sleep(1)
    sensor.heater = False
    print("Sensor Heater status =", sensor.heater)
    await asyncio.sleep(100)

async def Service_Loop():
    while True:
        if not (wifi.radio.ipv4_address is None):
            net_loop()
        await asyncio.sleep(0)

async def Sensor_Get(sensor, display):
    global led, server, mqtt_client, sdata
    while(True):
        await Blink(1) # 0.2 sec blink indicates start of data acquisition
        if not button.value:  # Button triggers restart routine
            Restart()
        # update sensor data
        try:
            sdata['temperature'] = sensor.temperature
            sdata['humidity'] = sensor.relative_humidity
            sdata['motion'] = pir.value
            sdata['motion_per_minute'].insert(sdata['motion'])
            sdata['microphone'] = getAudioLevel()
            # sdata['light'] = optical.lux

        except Exception as e:
            print("Exception " + str(e) + " during sensor data acquisition")

        # Output readings
        print(f"Temp={(sdata['temperature']):.1f}°C "
              + f"Hum={sdata['humidity']:.1f}% "
              + f"Mic={sdata['microphone']:.0f} "
              + f"Mot={sdata['motion_per_minute'].sum():.0f} "
              + f"Mem={gc.mem_free()/1024:.0f} kB")
        # print(f"Motion = {pir.value}")
        # print(f"Optical = {sdata['light']} lux")

        display.fill(0)
        display_text(display, f"Temperature = {(sdata['temperature'] * 1.8 + 32):.1f} F", 0)
        display_text(display, f"Humidity    = {sdata['humidity']:.1f}%", 1)
        display_text(display, f"Motion = {sdata['motion_per_minute'].sum()} /min", 3)
        display_text(display, f"Audio  = {sdata['microphone']:4.1f}", 4)

        # display_text(display, f"mem_free  = {gc.mem_free() / 1024:.0f}kB", 6)
        if not (wifi.radio.ipv4_address is None):
            display_text(display, f"IP: {wifi.radio.ipv4_address}", 7)
        display.show()
        net_update() # push mqtt data

        #print(f"mem_free: {gc.mem_free() / 1024:.0f}kB")
        gc.collect()
        #print("GC mem_free: %.0fkB" % gc.mem_free() / 1024)
        await asyncio.sleep(0.8)

async def Blink(n):
    for x in range(n):
        led.value = not led.value
        await asyncio.sleep(0.1)
        led.value = not led.value
        await asyncio.sleep(0.1)

async def main():
    tasks = []
    tasks.append(asyncio.create_task(Sensor_Get(sensor, display)))
    tasks.append(asyncio.create_task(Sensor_Heat(sensor)))
    tasks.append(asyncio.create_task(Service_Loop()))
    if os.getenv('CHECKMK_PORT'):
        tasks.append(asyncio.create_task(tcpserver(PORT)))

    await asyncio.gather(*tasks)

if __name__ =='__main__':
    try:
        display = Display_Init()
        sensor = Sensor_Init()
    except Exception as e:
        print("Exception " + str(e) + " during device initialization");
        StopApplication()

    asyncio.run(main())
