#!/usr/bin/python3
# MS Teams doesn't have a straightforward way to upload images directly
# Workaround:
# Upload an image to azure blob storage
# then post image URL to MS Teams via webhook

# USAGE:
# Set up variables in .env
#
#   pipenv run image_2_msteams.py ~/Pictures/Screenshots/screenshot.png
#

import os
import sys
import pymsteams
from azure.storage.blob import BlobServiceClient, BlobType, ContentSettings
## Future work: monitor a directory and post images as they appear
# import inotify.adapters
# from pathlib import Path

connection_string = os.environ.get('AZURE_CONNECTION_STRING')
container_name = os.environ.get('AZURE_CONTAINER_NAME')
blob_service_client = BlobServiceClient.from_connection_string(connection_string)

network = os.environ.get('ENV') or "Unset ENV"
msteams_webhook = os.environ.get('MSTEAMS_WEBHOOK')
debug = os.environ.get('DEBUG') or False

def upload_blob_file(imagefile, blob_service_client: BlobServiceClient, container_name: str):
    """Upload to Azure blob storage"""
    container_client = blob_service_client.get_container_client(container=container_name)
    content_settings=ContentSettings(content_type="image/png")
    with open(file=imagefile, mode="rb") as data:
        blob_client = container_client.upload_blob(
            name=f"screenshots/{os.path.basename(imagefile)}",
            data=data,
            blob_type=BlobType.BlockBlob,
            content_settings=content_settings,
            overwrite=True
            )
    if '?' in blob_client.url:
        return blob_client.url.split('?')[0]
    return blob_client.url


def msTeamsNotification(image_url):
    """Post to MS Teams webhook"""
    global msteams_webhook
    msTeamsMsg = pymsteams.connectorcard(msteams_webhook)
    msgSection = pymsteams.cardsection()
    msgSection.addImage(image_url, ititle="Azure Blob")
    msTeamsMsg.addSection(msgSection)
    msTeamsMsg.title('Screenshot')
    msTeamsMsg.text('PNG File')
    try:
        msTeamsMsg.send()
        assert msTeamsMsg.last_http_response.status_code == 200
    except Exception as e:
        print(f"Error sending to MS Teams: {str(e)}")


# Send notification to MSTeams when screenshot is added
def _main():
    # strip first element of argv array which is the script name
    for imagefile in sys.argv[1:]:
        url = upload_blob_file(imagefile, blob_service_client, container_name)
        print(url)
        msTeamsNotification(url)

    # i = inotify.adapters.Inotify()

    # print (f"Watching {Path(image_file).resolve()} for updates")
    # i.add_watch(Path(image_file).resolve().parent.as_posix())

    # for event in i.event_gen(yield_nones=False):
    #     (_, type_names, path, filename) = event

    #     if ( f"{path}/{filename}" == image_file
    #          and type_names[0] == 'IN_CLOSE_WRITE' ):
    #         print("PATH=[{}] FILENAME=[{}] EVENT_TYPES={}".format(
    #             path, filename, type_names))

    #         print (datetime.datetime.now())
    #         msTeamsNotification(image_file)


if __name__ == '__main__':
    _main()
