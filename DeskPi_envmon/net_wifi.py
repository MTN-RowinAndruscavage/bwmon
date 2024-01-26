import os
import wifi
import ipaddress
import socketpool
import binascii

# WiFi initialization
print(f"Connecting to WiFi... {os.getenv('CIRCUITPY_WIFI_SSID')}")
try:
    wifi.radio.connect(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD'))
except Exception as e:
    print("Wifi connect exception: " + str(e));

mac_address = binascii.hexlify(wifi.radio.mac_address).decode('utf-8')
human_readable_mac_address = ':'.join([mac_address[i:i+2] for i in range(0, len(mac_address), 2)])

print(f"My MAC addr: {human_readable_mac_address}")
print(f"My IP address is {wifi.radio.ipv4_address}")

# Test internet connectivity
ipv4 = ipaddress.ip_address('1.1.1.1')
internet_connected = False
try:
    print(f"Ping {ipv4} in {wifi.radio.ping(ipv4, timeout=2.0)} sec")
    internet_connected = True
except Exception as e:
    print(f"Ping exception: {str(e)}")

pool = socketpool.SocketPool(wifi.radio)


if __name__ == "__main__":
    print("Dropping to REPL")
