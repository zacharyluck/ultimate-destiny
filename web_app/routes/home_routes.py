from flask import Blueprint, jsonify, request, render_template
import pandas as pd
import random as rand

home_routes = Blueprint("home_routes", __name__)


@home_routes.route("/")
def index():
    return render_template('index.html')


@home_routes.route("/build", methods=['GET'])
def show_build():
    # get the data from the form on the main page
    userinput = dict(request.args)

    # copied code from pickletest.py
    # load dict from pickle thru pandas into dataframe
    d = pd.read_pickle('manifest.pickle')

    # set up some shortcuts because I'm not writing this
    d_buckets = d['DestinyInventoryBucketDefinition']
    d_items = d['DestinyInventoryItemDefinition']
    d_tiers = d['DestinyItemTierTypeDefinition']

    # which class the player is using, will be inputted via HTML form
    # Titan: 0, Hunter: 1, Warlock: 2
    class_choice = int(userinput['class'])

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
    # and exotic armors and save them to a new dict
    d_weapons = {}
    d_armors = {}
    for hash in d_items.keys():
        if d_items[hash]['itemType'] == 3:
            d_weapons[hash] = d_items[hash]
        if d_items[hash]['itemType'] == 2 and d_items[hash]['inventory']['tierTypeHash'] == TIER_EXOTIC:
            d_armors[hash] = d_items[hash]

    # d_weapons should now be a dict with every weapon in the game
    # seperate it into the three weapon categories or exotic weapons
    d_power = {}
    d_energy = {}
    d_kinetic = {}
    d_exotics = {}
    for hash in d_weapons.keys():
        # exclude class swords (nobody uses them anyway)
        if d_weapons[hash]['classType'] == 3:
            # legendary weapons
            if d_weapons[hash]['inventory']['tierTypeHash'] == TIER_LEGENDARY:
                # seperate by slot
                if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_POWER:
                    d_power[hash] = d_weapons[hash]
                if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_ENERGY:
                    d_energy[hash] = d_weapons[hash]
                if d_weapons[hash]['inventory']['bucketTypeHash'] == BUCKET_KINETIC:
                    d_kinetic[hash] = d_weapons[hash]
            # exotics
            if d_weapons[hash]['inventory']['tierTypeHash'] == TIER_EXOTIC:
                d_exotics[hash] = d_weapons[hash]

    # d_armors should have every exotic armor in the game
    # seperate them by which class they're for
    d_titan = {}
    d_hunter = {}
    d_warlock = {}
    for hash in d_armors.keys():
        if d_armors[hash]['classType'] == 0:
            d_titan[hash] = d_armors[hash]
        if d_armors[hash]['classType'] == 1:
            d_hunter[hash] = d_armors[hash]
        if d_armors[hash]['classType'] == 2:
            d_warlock[hash] = d_armors[hash]

    # test random selection capabilities
    # setup list of hashes for slots and exotic choice
    exotic_choice = rand.sample(list(d_exotics), 1)[0]
    kinetic_choice = rand.sample(list(d_kinetic), 1)[0]
    energy_choice = rand.sample(list(d_energy), 1)[0]
    power_choice = rand.sample(list(d_power), 1)[0]
    armor_choice = None
    class_string = None
    # armor selection
    if class_choice == 0:  # titan
        armor_choice = rand.sample(list(d_titan), 1)[0]
        class_string = 'Titan'
    if class_choice == 1:  # hunter
        armor_choice = rand.sample(list(d_hunter), 1)[0]
        class_string = 'Hunter'
    if class_choice == 2:  # warlock
        armor_choice = rand.sample(list(d_warlock), 1)[0]
        class_string = 'Warlock'

    # print the results
    choices = [
        d_kinetic[kinetic_choice]["displayProperties"]["name"],
        d_energy[energy_choice]["displayProperties"]["name"],
        d_power[power_choice]["displayProperties"]["name"],
        d_armors[armor_choice]["displayProperties"]["name"]
    ]

    # replace one slot with an exotic
    if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_KINETIC:
        choices[0] = d_exotics[exotic_choice]['displayProperties']['name']
    if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_ENERGY:
        choices[1] = d_exotics[exotic_choice]['displayProperties']['name']
    if d_exotics[exotic_choice]['inventory']['bucketTypeHash'] == BUCKET_POWER:
        choices[2] = d_exotics[exotic_choice]['displayProperties']['name']

    return render_template(
        'build.html', c_class=class_choice, c_kin=choices[0],
        c_ener=choices[1], c_pow=choices[2], c_arm=choices[3]
    )
