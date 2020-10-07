import requests
import zipfile
import os
import pickle
import json
import sqlite3


def get_manifest():
    manifest_url = 'http://www.bungie.net/Platform/Destiny/Manifest/'

    # get the manifest location
    r = requests.get(manifest_url)
    manifest = r.json()
    mani_url = 'http://www.bungie.net' + \
        manifest['Response']['mobileWorldContentPaths']['en']

    # download the file to a local zip
    r = requests.get(mani_url)
    with open('mani_zip', 'wb') as f:
        f.write(r.content)
    print('Download Complete.')
