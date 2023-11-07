import os, microcontroller, board
# Needed for ssl support:
#import ssl
#import adafruit_requests

import neopixel
pixels = neopixel.NeoPixel(board.GP22, 1)

from sensor_data import *
from net_wifi import *
# HTTPServer 
from adafruit_httpserver import Server, Request, Response, POST

# Initialize HTTP Server
server = Server(pool, "/static", debug=False)


font_family = "monospace"

def webpage():
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta http-equiv="Content-type" content="text/html;charset=utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="refresh" content="2">
    <style>
    html{{font-family: {font_family}; background-color: lightgrey;
    display:inline-block; margin: 0px auto; text-align: left;}}
      h1{{color: magenta; width: 200; word-wrap: break-word; padding: 2vh; font-size: 35px;}}
      p{{font-size: 1.5rem; width: 200; word-wrap: break-word;}}
      .button{{font-family: {font_family};display: inline-block;
      background-color: black; border: none;
      border-radius: 4px; color: white; padding: 16px 40px;
      text-decoration: none; font-size: 30px; margin: 2px; cursor: pointer;}}
      p.dotted {{margin: auto; width: 75%; font-size: 25px; text-align: left;}}
    </style>
    </head>
    <body>
    <title>5G Hub DeskPi PicoMate</title>
    <h1>Pico W HTTP Server</h1>
    <br>
    <table border="3">
    <tr>
    <td>Hardware</td>
    <td>{os.uname().machine}</td>
    </tr>
    <tr>
    <td>CircuitPython</td>
    <td>{os.uname().version}</td>
    </tr>
    
    <tr>
    <td>Temperature</td>
    <td><span style="color: magenta;">{sdata['temperature']:.2f}°C</span></p></td>
    </tr>
    
    <tr>
    <td>Humidity</td>
    <td><span style="color: magenta;">{sdata['humidity']:.2f}%</span></p></td>
    </tr>
    
    <tr>
    <td>Motion</td>
    <td><span style="color: magenta;">{sdata['motion']}</span></p></td>
    </tr>
    
    <tr>
    <td>Audio Level</td>
    <td><span style="color: magenta;">{sdata['microphone']:.1f}</span></p></td>
    </tr>
    
    </table>
    
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="LED ON" value="ON" type="submit">LED ON</button></a></p></form>
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="LED OFF" value="OFF" type="submit">LED OFF</button></a></p></form>
    <h1>Party?</h>
    <form accept-charset="utf-8" method="POST">
    <button class="button" name="party" value="party" type="submit">PARTY!</button></a></p></form>
    </body></html>
    """
    return html

@server.route("/")
def base(request: Request):  # pylint: disable=unused-argument
    return Response(request, f"{webpage()}", content_type='text/html')

@server.route("/get")
def basedata(request: Request):  # pylint: disable=unused-argument
    return Response(request, f"{jsondump()}", content_type='application/json')

#  Process website buttons
@server.route("/", POST)
def buttonpress(request: Request):
    raw_text = request.raw_request.decode("utf8")
    print(raw_text)

    if "ON" in raw_text:
        pixels[0] = (216, 0, 116)

    if "OFF" in raw_text:
        pixels[0] = (0, 0, 0)

#   if the party button was pressed
#     if "party" in raw_text:
#         #  toggle the parrot_pin value
#         parrot_pin.value = not parrot_pin.value
    #  reload site
    return Response(request, f"{webpage()}", content_type='text/html')


def net_loop():
    try:
        server.poll()
    except Exception as e:
        print("httpserver.poll Exception: " + str(e))

try:
    server.start(str(wifi.radio.ipv4_address))
    print("Listening on http://%s:80" % wifi.radio.ipv4_address)
#  if the server fails, restart the pico w
except OSError as e:
    print(f"OSError: {str(e)}")
    time.sleep(2)
    microcontroller.reset()


def net_update():
    pass

if __name__ == "__main__":
    while True:
        http_server_loop()
        sleep(0.1)
