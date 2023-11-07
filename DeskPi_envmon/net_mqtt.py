#########################################################################
#########################################################################
# WiFi

import os

# MQTT Client
import ssl
import adafruit_requests  # needed for MQTT SSL cert verification
import adafruit_minimqtt.adafruit_minimqtt as MQTT

# Import sdata and jsondump()
from sensor_data import *

# Connecto to wifi and load SocketPool pool
from net_wifi import *


def mqtt_connect(mqtt_client, userdata, flags, rc):
    print("Connected to MQTT Broker")
    print("Flags: {0}\n RC: {1}".format(flags, rc))

def mqtt_disconnect(mqtt_client, userdata, rc):
    print("Disconnected from MQTT Broker")

def mqtt_subscribe(mqtt_client, userdata, topic, granted_qos):
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))

def mqtt_unsubscribe(mqtt_client, userdata, topic, pid):
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))

def mqtt_publish(mqtt_client, userdata, topic, pid):
    #print("Published to {0} with PID {1}".format(topic, pid))
    pass

def mqtt_message(client, topic, message):
    #print("New message on topic {0}: {1}".format(topic, message))
    pass


if internet_connected and os.getenv('mqtt_broker'):
    # Set up a MiniMQTT Client
    mqtt_client = MQTT.MQTT(
        broker=os.getenv('mqtt_broker'),
        port=os.getenv('mqtt_port'),
        username=os.getenv('mqtt_username'),
        password=os.getenv('mqtt_password'),
        socket_pool=pool,
        is_ssl=True,
        ssl_context=ssl.create_default_context(),
    )

    # Connect callback handlers to mqtt_client
    mqtt_client.on_connect = mqtt_connect
    mqtt_client.on_disconnect = mqtt_disconnect
    mqtt_client.on_subscribe = mqtt_subscribe
    mqtt_client.on_unsubscribe = mqtt_unsubscribe
    mqtt_client.on_publish = mqtt_publish
    mqtt_client.on_message = mqtt_message

    print("Connecting to %s" % os.getenv('mqtt_broker'))
    try:
        mqtt_client.connect()
    except Exception as e:
        print("MQTT_client Connect Exception: " + str(e))

    mqtt_topic = os.getenv('mqtt_topic')
    print("Subscribing to %s" % mqtt_topic)
    try:
        mqtt_client.subscribe(mqtt_topic)
    except Exception as e:
        print("MQTT_client Subscribe Exception: " + str(e))


else:
    print("MQTT broker not configured")

def net_loop():
    try:
        mqtt_client.loop()
    except Exception as e:
        print("MQTT_loop Exception: " + str(e))
        
def net_update():
    mqtt_client.publish(mqtt_topic, jsondump())
        
def mqtt_close():
    print("Unsubscribing from %s" % mqtt_topic)
    try:
        mqtt_client.unsubscribe(mqtt_topic)
    except Exception as e:
        print("MQTT Unsubscribe Exception" + str(e))
        
    print("Disconnecting from %s" % mqtt_client.broker)
    try:
        mqtt_client.disconnect()
    except Exception as e:
        print("MQTT Disconnect Exception" + str(e))


if __name__ == "__main__":
    print("Shutting down mqtt")
    mqtt_close()