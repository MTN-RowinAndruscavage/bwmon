#!/usr/bin/python3

from slack_sdk.webhook import WebhookClient
from selenium import webdriver
import os, datetime
from pathlib import Path
import inotify.adapters
import simplejson as json

network = os.environ.get('ENV') or "Unset ENV"
slack_webhook = os.environ.get('SLACK_WEBHOOK')
sendNotification = os.environ.get('SEND') or True
debug = os.environ.get('DEBUG') or False
openBrowser = os.environ.get('OPENBROWSER') or True
speedtest_file = "/usr/lib/check_mk_agent/plugins/speedtest_data.json"

if openBrowser:
    browser=webdriver.Firefox()

def readData(filename):
    global debug, network, openBrowser, browser
    try:
        with open(filename) as json_data:
            sd = json.load(json_data)

        if 'result' not in sd:
            payload="Oops"

        if debug:
            print(json.dumps(sd, sort_keys=True, indent=2 * ' '))
    except Exception as e:
        print(f"Error loading json: {e}")
	return "Failed to parse json: {e}"

    url=''
    if 'url' in sd['result']:
        url = sd['result']['url']
    print (url, sd['server']['location'])

    if sd['download']['bandwidth'] > 1000:
        status = ":successful:"
    else:
        status = ":failed:"

    payload = f"Test-<{url}|{network}>: \
{status} \
DL {sd['download']['bandwidth'] / 125000 :.{0}f}, \
UL {sd['upload']['bandwidth'] / 125000 :.{0}f}, \
PING {sd['ping']['latency']:.{0}f}, \
JITTER {sd['ping']['jitter']:.{0}f}"

    print (payload)
    if openBrowser and url.startswith("https://"):
        ## webbrowser always opens a new tab
        # webbrowser.open(sd['result']['url'], new=0)
        try:
            browser.get(sd['result']['url'])
        except Exception as e:
            print(e)

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


# Send notification to Slack when speedtest data is updated
def _main():
    i = inotify.adapters.Inotify()

    print (f"Watching {Path(speedtest_file).resolve()} for updates")
    i.add_watch(Path(speedtest_file).resolve().parent.as_posix())

    for event in i.event_gen(yield_nones=False):
        (_, type_names, path, filename) = event

        if ( f"{path}/{filename}" == speedtest_file
             and type_names[0] == 'IN_CLOSE_WRITE' ):
            print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
                path, filename, type_names))

            print (datetime.datetime.now())
            slackNotification(readData(speedtest_file))


if __name__ == '__main__':
    _main()
