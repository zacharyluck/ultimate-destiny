from flask import Blueprint, jsonify, request, render_template
import pandas as pd
import random as rand
import pydest
from dotenv import load_dotenv
import os
from ast import literal_eval


# load environment variables
load_dotenv()
BUNGIE_API = os.getenv('BUNGIE_API')
# set up route connections
home_routes = Blueprint("home_routes", __name__)

# import data from generated files
df_weapons = pd.read_csv('weapons.csv', index_col='Unnamed: 0')
df_armors = pd.read_csv('armors.csv', index_col='Unnamed: 0')
df_subclasses = pd.read_csv('subclasses.csv', index_col='Unnamed: 0')
wordlist = pd.read_pickle('wordlist.pickle')
exclusions = pd.read_pickle('exclusions.pickle')
inclusions = pd.read_pickle('inclusions.pickle')
equip_hashes = pd.read_pickle('equiphashes.pickle')

# fix lists on subclasses dataframe
df_subclasses['treeNames'] = df_subclasses['treeNames'].apply(
    lambda x: literal_eval(x))
df_subclasses['treeTalents'] = df_subclasses['treeTalents'].apply(
    lambda x: literal_eval(x))
df_subclasses['grenadeNames'] = df_subclasses['grenadeNames'].apply(
    lambda x: literal_eval(x))

# create maps and
classmap = {
    0: 'titan',
    1: 'hunter',
    2: 'warlock'
}
subclassmap = {
    2: 'arc',
    3: 'solar',
    4: 'void'
}
EQUIP_KINETIC = equip_hashes[0]
EQUIP_ENERGY = equip_hashes[1]
EQUIP_POWER = equip_hashes[2]


def newbuild(class_):
    '''
    randomly generate a build from scratch

    inputs
    ------
    class_: enumeration for class chosen
    0 = titan, 1 = hunter, 2 = warlock
    '''
    # start by turning the class variable into an int
    class_ = int(class_)
    keywords = []
    # start by picking subclass
    # 2 = arc, 3 = solar, 4 = void
    element = rand.randint(2, 4)
    # get subclass
    subclass = df_subclasses[df_subclasses['element'] == element]
    subclass = subclass[subclass['class'] == class_]
    # this needs the [0] on the end because it returns a list
    d_subclass = subclass.to_dict(orient='records')[0]
    # get all subclass specific words
    # start by generating generic keywords
    subclass_keyword = classmap[class_]
    subclass_keyword += ' '
    subclass_keyword += subclassmap[element]
    subclass_keyword += ' subclass'
    keywords.append(subclass_keyword)
    keywords += [
        subclassmap[element] + ' damage',
        subclassmap[element] + ' abilities',
        subclassmap[element] + ' melee',
        subclassmap[element] + ' grenade'
    ]
    # pick subtree and also get subclass keywords
    subtree = rand.randint(0, 2)
    # super keyword
    keywords.append(d_subclass['superName'])
    # nade keywords
    keywords += d_subclass['grenadeNames']
    # name of the tree (not used I don't think)
    keywords.append(d_subclass['treeNames'][subtree])
    # names of abilities in trees
    keywords += d_subclass['treeTalents'][subtree]

    # pick weapons, lets start by setting up the output list
    # order is kinetic, energy, power, armor
    choices = [None, None, None, None]
    # start by picking the exotic weapon
    exotics = df_weapons[df_weapons['tierName'] == 'Exotic']
    exotic_pick = exotics.sample(n=1).to_dict(orient='records')[0]
    if exotic_pick['equipSlot'] == EQUIP_KINETIC:
        choices[0] = exotic_pick['hash']
    if exotic_pick['equipSlot'] == EQUIP_ENERGY:
        choices[1] = exotic_pick['hash']
    if exotic_pick['equipSlot'] == EQUIP_POWER:
        choices[2] = exotic_pick['hash']
    # get all weapons that aren't exotic
    weapons = df_weapons[df_weapons['tierName'] != 'Exotic']
    for n in range(3):
        if choices[n] is None:
            if n == 0:  # pick random kinetic weapon
                kinetic_choice = weapons[weapons['equipSlot'] == EQUIP_KINETIC].sample(
                    n=1).to_dict(orient='records')[0]
                choices[0] = kinetic_choice['hash']
            if n == 1:  # pick random energy weapon
                energy_choice = weapons[weapons['equipSlot'] == EQUIP_ENERGY].sample(
                    n=1).to_dict(orient='records')[0]
                choices[1] = energy_choice['hash']
            if n == 2:  # pick random power weapon
                power_choice = weapons[weapons['equipSlot'] == EQUIP_POWER].sample(
                    n=1).to_dict(orient='records')[0]
                choices[2] = power_choice['hash']
    # add weapon type keywords
    for n in range(3):
        # grab dict of choice
        choice = df_weapons[df_weapons['hash'] == choices[n]].to_dict(orient='records')[
            0]
        # grab weapon type keyword
        keywords.append(choice['weaponType'])
        if n == 1:  # grab energy damage keywords
            keyword = subclassmap[choice['damageType']]
            keyword += " damage"
            keywords.append(keyword)
    # I should have all the keywords I need now
    # lower-ize all the keywords
    keywords = [keyword.lower() for keyword in keywords]
    print(keywords)


@home_routes.route("/")
def index():
    return render_template('index.html')


@home_routes.route("/build", methods=['GET'])
def show_build():
    # get the data from the form on the main page
    userinput = dict(request.args)

    # determine what kind of build it is
    if 'newbuild' in userinput:
        newbuild(userinput['newbuild'])

    return render_template(
        'build.html', c_class=class_name, c_kin=names[0],
        c_ener=names[1], c_pow=names[2], c_arm=names[3],
        c_kin_icon=icons[0], c_ener_icon=icons[1], c_pow_icon=icons[2],
        c_arm_icon=icons[3]
    )
