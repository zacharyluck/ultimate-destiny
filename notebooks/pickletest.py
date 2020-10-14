# this file is just so I can explore what is inside of
# manifest.pickle, as well as the code that will be used to
# load the pickled dict later.

import pandas as pd
import random as rand


# load dict from pickle thru pandas into dataframe
d = pd.read_pickle('manifest.pickle')

# set up some shortcuts because I'm not writing this
d_buckets = d['DestinyInventoryBucketDefinition']
d_items = d['DestinyInventoryItemDefinition']
d_tiers = d['DestinyItemTierTypeDefinition']

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

# go through every hash in d_items and grab all the weapons
# and save them to a new dict
d_weapons = {}
for hash in d_items.keys():
    if d_items[hash]['itemType'] == 3:
        d_weapons[hash] = d_items[hash]

# d_weapons should now be a dict with every weapon in the game
# seperate it into the three weapon categories or exotic weapons
d_power = {}
d_energy = {}
d_kinetic = {}
d_exotics = {}
for hash in d_weapons.keys():
    if d_weapons[hash]['inventory']['tierTypeHash'] == TIER_LEGENDARY:
        if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_POWER:
            d_power[hash] = d_weapons[hash]
        if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_ENERGY:
            d_energy[hash] = d_weapons[hash]
        if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_KINETIC:
            d_kinetic[hash] = d_weapons[hash]
    if d_weapons[hash]['inventory']['tierTypeHash'] == TIER_EXOTIC:
        d_exotics[hash] = d_weapons[hash]

# test random selection capabilities
# setup list of hashes for slots and exotic choice
exotic_choice = rand.sample(list(d_exotics), 1)[0]
kinetic_choice = rand.sample(list(d_kinetic), 1)[0]
energy_choice = rand.sample(list(d_energy), 1)[0]
power_choice = rand.sample(list(d_power), 1)[0]

# print the results
choices = [
    d_kinetic[kinetic_choice]["displayProperties"]["name"],
    d_energy[energy_choice]["displayProperties"]["name"],
    d_power[power_choice]["displayProperties"]["name"]
]

# replace one slot with an exotic
if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_KINETIC:
    choices[0] = d_exotics[exotic_choice]['displayProperties']['name']
if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_ENERGY:
    choices[1] = d_exotics[exotic_choice]['displayProperties']['name']
if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_POWER:
    choices[2] = d_exotics[exotic_choice]['displayProperties']['name']

print(
    f'Kinetic Weapon: {choices[0]}')
print(
    f'Energy Weapon: {choices[1]}')
print(
    f'Power Weapon: {choices[2]}')
