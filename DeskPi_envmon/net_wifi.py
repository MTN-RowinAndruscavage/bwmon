import os
import wifi
import ipaddress
import socketpool


# WiFi initialization
print(f"Connecting to WiFi... {os.getenv('CIRCUITPY_WIFI_SSID')}")
try:
    wifi.radio.connect(
        os.getenv('CIRCUITPY_WIFI_SSID'),
        os.getenv('CIRCUITPY_WIFI_PASSWORD'))
except Exception as e:
    print("Wifi connect exception: " + str(e));

print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("My IP address is", wifi.radio.ipv4_address)

# Test internet connectivity
ipv4 = ipaddress.ip_address('8.8.8.8')
internet_connected = False
try:
    print(f"Ping {ipv4} in {wifi.radio.ping(ipv4, timeout=1.0)} sec")
    internet_connected = True
except Exception as e:
    print(f"Ping exception: {str(e)}")
    
pool = socketpool.SocketPool(wifi.radio)


if __name__ == "__main__":
    print("Dropping to REPL")
    
