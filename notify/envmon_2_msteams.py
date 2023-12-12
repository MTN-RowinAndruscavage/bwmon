#!/usr/bin/python3

import os, time
import simplejson as json
import requests
import pymsteams

sensors = [
    {
        "name": "env-dr1500",
        "ip": "192.168.0.3"
    },
    {
        "name": "env-cage",
        "ip": "192.168.0.4"
    }
]

msteams_webhook = os.environ.get('MSTEAMS_WEBHOOK')
sendNotification = os.environ.get('SEND') or True
debug = os.environ.get('DEBUG') or False

def readData(name, ip):
    global debug

    try:
        response = requests.get(f'http://{ip}/get')
    except Exception as e:
        print(f"Error reading http://{ip}/get : {str(e)}")
    sd = response.json()

    if debug:
        print(json.dumps(sd, sort_keys=True, indent=2 * ' '))

    if 'temperature' in sd:
        status = "✅"
        payload = f"{name}: \
{status} \
Temp: {sd['temperature'] * 1.8 + 32 :.{1}f}°F \
Humidity: {sd['humidity'] :.{1}f}% \
Mic: {sd['microphone']:.{0}f}"
    else:
        status = "❌"
        payload = f"{name}: \
{status}"

    print (payload)

    return payload


# Send hourly notifications to MS Teams
def _main():
    while True:
        msTeamsMsg = pymsteams.connectorcard(msteams_webhook)
        for s in sensors:
            section = pymsteams.cardsection()
            try:
                section.text(readData(s['name'], s['ip']))
            except Exception as e:
                print(f"Error polling {s['name']}: {str(e)}")
            msTeamsMsg.addSection(section)

        msTeamsMsg.summary("Environmental monitor")
        if sendNotification:
            try:
                msTeamsMsg.send()
            except Exception as e:
                print(f"Error sending to MS Teams: {str(e)}")
            assert msTeamsMsg.last_http_response.status_code == 200

        time.sleep(3600)

if __name__ == '__main__':
    _main()
