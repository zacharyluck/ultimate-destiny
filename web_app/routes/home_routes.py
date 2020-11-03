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

# fix lists on subclasses dataframe
df_subclasses['treeNames'] = df['treeNames'].apply(lambda x: literal_eval(x))
df_subclasses['treeTalents'] = df['treeTalents'].apply(
    lambda x: literal_eval(x))
df_subclasses['grenadeNames'] = df['grenadeNames'].apply(
    lambda x: literal_eval(x))

# pre-create class and subclass maps for keywords
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


def newbuild(class_):
    '''
    randomly generate a build from scratch

    inputs
    ------
    class_: enumeration for class chosen
    0 = titan, 1 = hunter, 2 = warlock
    '''
    keywords = []
    # start by picking subclass
    # 2 = arc, 3 = solar, 4 = void
    element = rand.randint(2, 4)
    # get subclass
    subclass = df_subclasses[
        (df_subclasses['element'] == element &
         df_subclasses['class'] == class_)
    ]
    d_subclass = subclass.to_dict(orient='records')
    # get all subclass specific words
    # start by generating generic keywords
    keywords.append(classmap[class_] + ' ' +
                    subclassmap[element] + ' subclass')
    keywords += [
        subclassmap[element] + ' damage',
        subclassmap[element] + ' abilities',
        subclassmap[element] + ' melee',
        subclassmap[element] + ' grenade'
    ]
    # get grenades
    keywords += d_subclass
    # pick subtree
    subtree = rand.randint(0, 2)
    for hash in d_subclass:
        keywords += d_subclass[hash]['superName']
        keywords += d_subclass[hash]['treeNames'][subtree]
        keywords += d_subclass[hash]['treeTalents'][subtree]

    # pick weapons, lets start by setting up the output list
    choices = []
    # start by picking the exotic weapon
    exotics = df_weapons[df_weapons['tierHash'] == 'Exotic']


@home_routes.route("/")
def index():
    return render_template('index.html')


@home_routes.route("/build", methods=['GET'])
def show_build():
    # get the data from the form on the main page
    userinput = dict(request.args)

    # determine what kind of build it is
    if 'newbuild' in userinput

    return render_template(
        'build.html', c_class=class_name, c_kin=names[0],
        c_ener=names[1], c_pow=names[2], c_arm=names[3],
        c_kin_icon=icons[0], c_ener_icon=icons[1], c_pow_icon=icons[2],
        c_arm_icon=icons[3]
    )
