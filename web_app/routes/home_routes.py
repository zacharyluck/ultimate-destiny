from flask import Blueprint, jsonify, request, render_template
import pandas as pd
import random as rand
import pydest
from dotenv import load_dotenv
import os

# load environment variables
load_dotenv()
BUNGIE_API = os.getenv('BUNGIE_API')
# set up route connections
home_routes = Blueprint("home_routes", __name__)


@home_routes.route("/")
def index():
    return render_template('index.html')


@home_routes.route("/build", methods=['GET'])
def show_build():
    # get the data from the form on the main page
    userinput = dict(request.args)

    # import data from generated csvs
    df_weapons = pd.read_csv('weapons.csv', index_col='Unnamed: 0')
    df_armors = pd.read_csv('armors.csv', index_col='Unnamed: 0')

    return render_template(
        'build.html', c_class=class_name, c_kin=names[0],
        c_ener=names[1], c_pow=names[2], c_arm=names[3],
        c_kin_icon=icons[0], c_ener_icon=icons[1], c_pow_icon=icons[2],
        c_arm_icon=icons[3]
    )
