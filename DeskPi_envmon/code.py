# Sensor readings for DeskPi PicoMate from
# https://deskpi.com/blogs/learn/deskpi-picomate-user-manual-and-sources

# Network server from
# https://learn.adafruit.com/pico-w-http-server-with-circuitpython/code-the-pico-w-http-server

# From https://github.com/Braiuz/RaspberryPiPico_WeatherStation/tree/main
# ported from micropython to adafruit circuitpython

import os, microcontroller, board, busio
import time
import gc


# Can't find this optical sensor driver
# from adafruit_ltr381rgb import LTR381RGB
from mic import *

from sensor_data import *

# There's only enough memory to run one or the other
if os.getenv('mqtt_broker'):
    from net_mqtt import *
else:    
    from net_httpserver import *

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




# something global in these 2 sensors conflicts with mqtt (!)
from adafruit_sht31d import SHT31D
from adafruit_ssd1306 import SSD1306_I2C

def Sensor_Get(sensor, display):
    global led, server, mqtt_client, sdata
    loopcount = 100  # trigger sensor heater on first iteration
    while(True):
        if not (wifi.radio.ipv4_address is None):
            net_loop()
            gc.collect()
        loopcount += 1
        time.sleep(0.1)
        # update network at 10Hz, update sensor / display at ~1Hz
        if not (loopcount % 10):
            next
    
        Blink(1) # 0.2 sec blink indicates start of data acquisition
        if not button.value:  # Button triggers restart routine
            Restart()
        # update sensor data
        try:
            sdata['temperature'] = sensor.temperature
            sdata['humidity'] = sensor.relative_humidity
            sdata['motion'] = pir.value
            sdata['microphone'] = getAudioLevel()                  
            # sdata['light'] = optical.lux
            
        except Exception as e:
            print("Exception " + str(e) + " during sensor data acquisition")
            
        # Output readings
        print(f"Temperature = {(sdata['temperature'] * 1.8 + 32):.1f}°F "
              + f"Humidity = {sdata['humidity']:.1f}% Microphone = {sdata['microphone']}")
        # print(f"Motion = {pir.value}")
        # print(f"Optical = {sdata['light']} lux")
        
        display.fill(0)
        display_text(display, f"Temperature = {(sdata['temperature'] * 1.8 + 32):.1f} F", 0)
        display_text(display, f"Humidity    = {sdata['humidity']:.1f}%", 1)
        display_text(display, f"Motion = {sdata['motion']}", 3)
        display_text(display, f"Audio  = {sdata['microphone']:4.1f}", 4)
        
        # display_text(display, f"mem_free  = {gc.mem_free() / 1024:.0f}kB", 6)
        if not (wifi.radio.ipv4_address is None):
            display_text(display, f"IP: {wifi.radio.ipv4_address}", 7)
        display.show()


        net_update()

        # Burn off condensation from humidity sensor about every 10 sec
        if loopcount > 100:
            loopcount = 0
            sensor.heater = True
            print("Sensor Heater status =", sensor.heater)
            time.sleep(1)
            sensor.heater = False
            print("Sensor Heater status =", sensor.heater)
            
            
        #print(f"mem_free: {gc.mem_free() / 1024:.0f}kB")
        gc.collect()
        #print("GC mem_free: %.0fkB" % gc.mem_free() / 1024)

            
def Blink(n):
    for x in range(n):
        led.value = not led.value
        time.sleep(0.1)
        led.value = not led.value
        time.sleep(0.1)

if __name__ =='__main__':
    time.sleep(1)
    try:
        display = Display_Init()
        sensor = Sensor_Init()
        Sensor_Get(sensor, display)
        
    except Exception as e:
        print("Exception " + str(e) + " during sensor data acquisition");
        StopApplication()
