#!/usr/bin/python3

from selenium import webdriver
import os, datetime
from pathlib import Path
import inotify.adapters
import simplejson as json
import pymsteams

network = os.environ.get('ENV') or "Unset ENV"
msteams_webhook = os.environ.get('MSTEAMS_WEBHOOK')
sendNotification = os.environ.get('SEND') or True
debug = os.environ.get('DEBUG') or False
openBrowser = os.environ.get('OPENBROWSER') or False
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
        print(f"Error loading json file: {e}")
        return f"Failed to parse json: {e}"

    url=''
    if 'url' in sd['result']:
        url = sd['result']['url']
    print (url, sd['server']['location'])

    if sd['download']['bandwidth'] > 125000:
        status = "✅"
    else:
        status = "❗"

    payload = f"Test-{network}: \
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

    return (payload,url)


def msTeamsNotification(payload,url):
    global msteams_webhook, sendNotification
    # Set environment SEND=False to skip notification
    if sendNotification:
        msTeamsMsg = pymsteams.connectorcard(msteams_webhook)
        msTeamsMsg.text(payload)
        if url != '':
            msTeamsMsg.addLinkButton("Ookla Summary", url)
        try:
            msTeamsMsg.send()
            assert msTeamsMsg.last_http_response.status_code == 200
        except Exception as e:
            print(f"Error sending to MS Teams: {str(e)}")
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
            (payload, url) = readData(speedtest_file)
            msTeamsNotification(payload, url)


if __name__ == '__main__':
    _main()
