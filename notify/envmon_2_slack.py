#!/usr/bin/python3

from slack_sdk.webhook import WebhookClient
import os, time
import simplejson as json
import requests

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

slack_webhook = os.environ.get('SLACK_WEBHOOK')
sendNotification = os.environ.get('SEND') or True
debug = os.environ.get('DEBUG') or False

def readData(name, ip):
    global debug

    response = requests.get(f'http://{ip}/get')
    sd = response.json()

    if debug:
        print(json.dumps(sd, sort_keys=True, indent=2 * ' '))

    if 'temperature' in sd:
        status = ":successful:"
    else:
        status = ":failed:"

    payload = f"{name}: \
{status} \
Temp: {sd['temperature'] * 1.8 + 32 :.{1}f}°F \
Humidity: {sd['humidity'] :.{1}f}% \
Mic: {sd['microphone']:.{0}f}"

    print (payload)

    return payload


def slackNotification(payload):
    global slack_webhook, sendNotification
    # Set environment SEND=False to skip notification
    if sendNotification:
        webhook = WebhookClient(slack_webhook)
        response = webhook.send(
            text = "fallback",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": payload
                    }
                }
            ]
        )
        assert response.status_code == 200
        assert response.body == "ok"
        return


# Send hourly notifications to Slack
def _main():
    while True:
        for s in sensors:
            try:
                slackNotification(readData(s['name'], s['ip']))
            except e:
                print(f"Error polling {s['name']}: {str(e)}")
        time.sleep(3600)

if __name__ == '__main__':
    _main()
