# test file to see how grabbing the manifest data from
# the bungie API works; this code will eventually be transferred
# into a python file in routes/
#
# this file creates three files:
# mani_zip, which is a zipped version of the game manifest
# Manifest.content, which is the manifest in SQLite form
# manifest.pickle, the manifest in dict form.

import requests
import zipfile
import os
import pickle
import json
import sqlite3
import pydest
import asyncio
from dotenv import load_dotenv


# load environment variables
load_dotenv()
BUNGIE_API = os.getenv('BUNGIE_API')

# grab async loop for pydest
loop = asyncio.get_event_loop()


async def pull_manifest():
    # open API connection
    destiny = pydest.Pydest(BUNGIE_API)
    # grab the manifest data
    res = await destiny.api._get_request('https://www.bungie.net/Platform/Destiny2/Manifest/')
    # close API connection
    await destiny.close()
    # return manifest data
    return res


async def pull_sql(manifest):
    # open API connection
    destiny = pydest.Pydest(BUNGIE_API)
    # grab SQL data from manifest
    URL = 'https://www.bungie.net' + \
        manifest['Response']['mobileWorldContentPaths']['en']
    print('Pulling data from '+URL)
    res = await destiny.api._get_request(URL)
    # close API connection
    await destiny.close()
    # return manifest data
    return res


def get_manifest():
    # grab manifest data
    manifest = loop.run_until_complete(pull_manifest())
    print('Manifest JSON downloaded.')

    # grab SQL URL from manifest
    URL = 'https://www.bungie.net' + \
        manifest['Response']['mobileWorldContentPaths']['en']

    # use requests to download manifest SQLs
    r = requests.get(URL)
    with open('mani_zip', 'wb') as f:
        f.write(r.content)
    print('Manifest downloaded.')

    # extract the file contents into its proper form
    with zipfile.ZipFile('mani_zip') as f:
        name = f.namelist()
        f.extractall()
    os.rename(name[0], 'Manifest.content')
    print('Manifest unzipped.')


# tables list, just here in case I need it
hashes = [
    'DestinyEnemyRaceDefinition',
    'DestinyPlaceDefinition',
    'DestinyActivityDefinition',
    'DestinyActivityTypeDefinition',
    'DestinyClassDefinition',
    'DestinyGenderDefinition',
    'DestinyInventoryBucketDefinition',
    'DestinyRaceDefinition',
    'DestinyTalentGridDefinition',
    'DestinyUnlockDefinition',
    'DestinyMaterialRequirementSetDefinition',
    'DestinySandboxPerkDefinition',
    'DestinyStatGroupDefinition',
    'DestinyFactionDefinition',
    'DestinyVendorGroupDefinition',
    'DestinyItemCategoryDefinition',
    'DestinyDamageTypeDefinition',
    'DestinyActivityModeDefinition',
    'DestinyMedalTierDefinition',
    'DestinyAchievementDefinition',
    'DestinyActivityGraphDefinition',
    'DestinyBondDefinition',
    'DestinyCollectibleDefinition',
    'DestinyDestinationDefinition',
    'DestinyEquipmentSlotDefinition',
    'DestinyStatDefinition',
    'DestinyInventoryItemDefinition',
    'DestinyItemTierTypeDefinition',
    'DestinyLocationDefinition',
    'DestinyLoreDefinition',
    'DestinyMetricDefinition',
    'DestinyObjectiveDefinition',
    'DestinyPlugSetDefinition',
    'DestinyPowerCapDefinition',
    'DestinyPresentationNodeDefinition',
    'DestinyProgressionDefinition',
    'DestinyProgressionLevelRequirementDefinition',
    'DestinyRecordDefinition',
    'DestinySackRewardItemListDefinition',
    'DestinySandboxPatternDefinition',
    'DestinySeasonDefinition',
    'DestinySeasonPassDefinition',
    'DestinySocketCategoryDefinition',
    'DestinySocketTypeDefinition',
    'DestinyTraitDefinition',
    'DestinyTraitCategoryDefinition',
    'DestinyVendorDefinition',
    'DestinyMilestoneDefinition',
    'DestinyActivityModifierDefinition',
    'DestinyReportReasonCategoryDefinition',
    'DestinyArtifactDefinition',
    'DestinyBreakerTypeDefinition',
    'DestinyChecklistDefinition',
    'DestinyEnergyTypeDefinition',
    'DestinyHistoricalStatsDefinition'
]

# the tables list I'm actually using
hashes_trunc = [
    'DestinyInventoryItemDefinition',
    'DestinyEquipmentSlotDefinition',
    'DestinyTalentGridDefinition',
    'DestinyLoreDefinition'
]

# build dict from sql manifest and pickle it


def build_dict(hash_dict):
    # manifest is downloaded as SQL, connect to it
    conn = sqlite3.connect('manifest.content')
    print('Connected to manifest file.')

    # create cursor
    curs = conn.cursor()

    data = {}
    # go through each table in the manifest
    for tablename in hash_dict:
        # get a list of all JSONs from table
        curs.execute('SELECT json from '+tablename)
        print(f'Generating {tablename} dictionary...')

        # this returns a list of tuples with only one item
        items = curs.fetchall()

        # extract data from within tuple, listify
        item_jsons = [json.loads(item[0]) for item in items]

        # create dict with the hashes as keys and jsons as values
        item_dict = {}
        for item in item_jsons:
            item_dict[item['hash']] = item

        # add it back to the main data dict
        data[tablename] = item_dict

    print('Dictionaries generated.')
    return data

# main run loop starts here


# check if pickle exists, and create one if it doesn't
if os.path.isfile('manifest.content') == False:
    # download manifest and unpack it
    get_manifest()
    data = build_dict(hashes_trunc)
    with open('manifest.pickle', 'wb') as f:
        pickle.dump(data, f)
        print("'manifest.pickle' created.")
else:
    print("'manifest.pickle' already exists.")

print('Testing data retrieval: Pulling data for "Ace of Spades"')
hash = 347366834
ace = data['DestinyInventoryItemDefinition'][hash]
print(f'Name: {ace["displayProperties"]["name"]}')
print(f'Type: {ace["itemTypeDisplayName"]}')
print(f'Tier: {ace["inventory"]["tierTypeName"]}')

# close loop
loop.close()
