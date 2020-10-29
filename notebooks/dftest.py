# notebook file to test turning the pickled dict
# into pandas dataframes with all the important info
# as well as new info that I need to create to make
# builds make more sense

import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import pickle

# start by unpickling the dicts
d = pd.read_pickle('manifest.pickle')


# set up some shortcuts because I'm not writing this
d_buckets = d['DestinyInventoryBucketDefinition']
d_items = d['DestinyInventoryItemDefinition']
d_tiers = d['DestinyItemTierTypeDefinition']
d_talents = d['DestinyTalentGridDefinition']
d_lores = d['DestinyLoreDefinition']

# start by grabbing inventory bucket defs for weapons
# I'm doing this to ensure that, in the case of a manifest
# re-hash, that these hash values don't need to be manually
# updated
BUCKET_POWER = None
BUCKET_ENERGY = None
BUCKET_KINETIC = None
for hash in d_buckets.keys():
    if 'displayProperties' not in d_buckets[hash]:
        continue
    if 'name' not in d_buckets[hash]['displayProperties']:
        continue
    if d_buckets[hash]['displayProperties']['name'] == 'Power Weapons':
        BUCKET_POWER = hash
    if d_buckets[hash]['displayProperties']['name'] == 'Energy Weapons':
        BUCKET_ENERGY = hash
    if d_buckets[hash]['displayProperties']['name'] == 'Kinetic Weapons':
        BUCKET_KINETIC = hash

# grab rarity hash values also
TIER_LEGENDARY = None
TIER_EXOTIC = None
for hash in d_tiers.keys():
    if d_tiers[hash]['displayProperties']['name'] == 'Legendary':
        TIER_LEGENDARY = hash
    if d_tiers[hash]['displayProperties']['name'] == 'Exotic':
        TIER_EXOTIC = hash

# set up weapon and exotic armor dataframes
d_weapons = {}
d_armors = {}
d_subclasses = {}
for hash in d_items.keys():
    if d_items[hash]['itemType'] == 3:
        # requirements: itemType is 3 (enum for Weapon)
        # initialize entry
        entry = {}
        # grab hash
        entry['hash'] = hash
        # grab name of item
        entry['name'] = d_items[hash]['displayProperties']['name']
        # grab icon path
        entry['icon'] = d_items[hash]['displayProperties']['icon']
        # get rarity hash
        entry['tierHash'] = d_items[hash]['inventory']['tierTypeHash']
        # get weapon type
        entry['weaponType'] = d_items[hash]['itemTypeDisplayName']
        # get equipping slot hash
        entry['equipSlot'] = d_items[hash]['equippingBlock']['equipmentSlotTypeHash']
        # get ammo type
        entry['ammoType'] = d_items[hash]['equippingBlock']['ammoType']
        # get class requirement
        entry['class'] = d_items[hash]['classType']
        # add it to the list, season number will be extracted later
        d_weapons[hash] = entry

    if d_items[hash]['itemType'] == 2 and d_items[hash]['inventory']['tierTypeHash'] == TIER_EXOTIC and 'collectibleHash' in d_items[hash]:
        # requirements: itemType is 2 (enum for armor)
        # tierTypeHash (rarity) is exotic
        # collectibleHash can be found in the item
        # (armor 2.0 items only so no dupes)
        entry = {}
        # grab hash
        entry['hash'] = hash
        # grab name of item
        entry['name'] = d_items[hash]['displayProperties']['name']
        # grab icon path
        entry['icon'] = d_items[hash]['displayProperties']['icon']
        # get class requirement
        entry['class'] = d_items[hash]['classType']
        # get exotic perk description
        perkhash = d_items[hash]['sockets']['socketEntries'][3]['singleInitialItemHash']
        entry['ability'] = d_items[perkhash]['displayProperties']['description']
        # fix up Aeon armor ability entries
        entry['ability'] = re.sub('[\n].+', '', entry['ability'])
        entry['ability'] = entry['ability'].replace('\n', '')
        # append to armor list
        d_armors[hash] = entry

    if d_items[hash]['itemType'] == 16:
        # requirements: itemType is 16 (enum for subclass)
        entry = {}
        # grab hash
        entry['hash'] = hash
        # grab name of item
        entry['name'] = d_items[hash]['displayProperties']['name']
        # grab icon path
        entry['icon'] = d_items[hash]['displayProperties']['icon']
        # get element
        entry['element'] = d_items[hash]['talentGrid']['hudDamageType']
        # get class requirement
        entry['class'] = d_items[hash]['classType']
        # get talent grid hash
        talent_hash = d_items[hash]['talentGrid']['talentGridHash']
        # use it to get default super and name and text of abilities
        # in all three subclass trees.
        talent_nodes = d_talents[talent_hash]['nodes']
        entry['superName'] = talent_nodes[10]['steps'][0]['displayProperties']['name']
        treeTalents = []
        treeNames = []
        # set up treeTalents such that it's a list 3 elements long
        # and each element is a list of names and descriptions of
        # talents in that specific tree
        #
        # I apologize, future self, this was the only way I could
        # think of doing it
        for n in range(11, 24):
            if n == 19:
                # skip 19 since it's blank, idk why
                continue
            if n == 11 or n == 15 or n == 20:
                # these node numbers indicate the starts of the
                # subclass trees, please don't change these Bungie.
                #
                # I'm gonna add an extra thing here to grab the
                # names of the trees themselves so that they
                # match up with the skills in treeTalents

                # create a new tree for talent node names and descs
                tree = []

                # search through the talentGrid groups and grab
                # the loreHash
                loreHash = None
                for group in d_talents[talent_hash]['groups']:
                    # construct list of nodeHashes from the group
                    nodeHashes = [x for x in d_talents[talent_hash]
                                  ['groups'][group]['nodeHashes']]
                    # check if the current number is in the nodehash list
                    if n in nodeHashes:
                        loreHash = d_talents[talent_hash]['groups'][group]['loreHash']
                        treeNames.append(
                            d_lores[loreHash]['displayProperties']['name'])
                        # since I don't wanna run this when unneeded
                        break
            tree.append(talent_nodes[n]['steps'][0]
                        ['displayProperties']['name'])
            if n == 14 or n == 18 or n == 23:
                # these indicate the ends of trees
                treeTalents.append(tree)
        entry['treeNames'] = treeNames
        entry['treeTalents'] = treeTalents
        # add to dict
        d_subclasses[hash] = entry

# pull season data from light.gg for legendary weapons (i'm sorry)
# some weapons will be updated multiple times since they're re-released
# since it starts from season one it'll have the latest season always
baseurl = 'https://www.light.gg/db/all/?page={page}&f=5:1({season}),2,4(5)'

page = 1
season = 1


def getpage(page, season):
    # quick func to grab this stuff so I don't have to copy/paste
    r = requests.get(baseurl.format(page=page, season=season))
    soup = BeautifulSoup(r.text, 'html.parser')
    leg_list = [a.get('href')
                for a in soup.find_all('a', class_='text-legendary')]
    return leg_list


urllist = getpage(page, season)

while urllist:
    print(f'Getting data: Season {season}, Page {page}.')
    # go through every legendary item link on the page
    for url in urllist:
        hash = int(url.split('/')[3])
        d_weapons[hash]['season'] = season

    # go to the next page
    page += 1
    # check if the page works
    urllist = getpage(page, season)
    if not urllist:
        # out of pages, reset pages, increment season
        page = 1
        season += 1
        urllist = getpage(page, season)
        # from here, if the season is too high, the loop should stop

# manually created dictionary to catch keywords in armor
# effect descriptions, general-purpose armor should come back
# with no matching keywords
wordlist = [
    # catch generic subclass exotics
    'arc abilities', 'void abilities', 'solar abilities',
    'arc melee', 'void melee', 'solar melee', 'blink',
    'arc grenade', 'void grenade', 'solar grenade',  # <- will catch sunbracers
    'arc bolt grenade', 'skip grenade', 'flux grenade',  # grenade-specifics
    'lightning grenade', 'flashbang grenade', 'pulse grenade',
    'storm grenade', 'tripmine grenade', 'incindiary grenade',
    'swarm grenade', 'fusion grenade', 'thermite grenade',
    'firebolt grenade', 'voidwall grenade', 'vortex grenade',
    'spike grenade', 'suppressor grenade', 'magnetic grenade',
    'scatter grenade', 'axion bolt', 'invisibility',
    'knives', 'smoke bomb', 'shield bash',  # melee-specifics
    'seismic strike', 'hammer strike', 'knife',
    'arc staff', 'whirlwind guard', 'golden gun',  # super-specifics
    'blade barrage', 'deadfall', 'moebius quiver',
    'spectral blades', 'sentinel shield', 'ward of dawn',
    'fists of havoc', 'sun warrior', 'nova bomb',
    'daybreak', 'well of radiance', 'stormtrance',
    'chaos reach',
    'auto rifle', 'submachine gun', 'sword', 'bow',  # weapon-specifics
    'sidearm', 'hand cannon'
]
exclusions = {  # replace supers so that certain keywords aren't found
    'chaos reach': ['stormtrance'],
    'thundercrash': ['fists of havoc'],
    'blade barrage': ['golden gun'],
    'spectral blades': ['deadfall', 'moebius quiver'],
    'nova warp': ['nova bomb'],
    'well of radiance': ['dawnblade']
}
inclusions = {  # add additional keywords to add catches
    'warlock void subclass': 'blink',
    'hunter void subclass': 'invisibility',
    'knife': 'knives',
    'snare bomb': 'smoke bomb',
    'corrosive smoke': 'smoke bomb',
    'vanish in smoke': 'smoke bomb',
    'magnitude': 'not_armamentarium'
}

# all weapons should have a season stat now
df_weapons = pd.DataFrame(d_weapons).T
df_armors = pd.DataFrame(d_armors).T
df_subclasses = pd.DataFrame(d_subclasses).T

df_weapons.to_csv('weapons.csv')
df_armors.to_csv('armors.csv')
df_subclasses.to_csv('subclasses.csv')

with open('wordlist.pickle', 'wb') as f:
    pickle.dump(wordlist, f)
    print("'wordlist.pickle' created.")
with open('exclusions.pickle', 'wb') as f:
    pickle.dump(exclusions, f)
    print("'exclusions.pickle' created.")
with open('inclusions.pickle', 'wb') as f:
    pickle.dump(inclusions, f)
    print("'inclusions.pickle' created.")
