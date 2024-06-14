import json
import os
import requests
import urllib3
import pandas as pd
from utils import read_config
from create_df import fetch_dataframe, extract_run_data
from plot_data import plot_all

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

path = os.path.dirname(os.path.realpath(__file__))
tick_mark = "\u2714"

def get_access_token(client_id, client_secret):
    """ Request access token using client id, client secret and refresh token values """   
    payload = {
        'client_id': client_id,
        'client_secret': client_secret,
        'refresh_token': '55aa876957c95e4dbda77ed2a8572eb3d0101bff',
        'grant_type': "refresh_token",
        'f': 'json'
    }
    print("Requesting Token...", end=" ")
    auth_url = "https://www.strava.com/oauth/token"
    json_result = requests.post(auth_url, data=payload, verify=False)
    print(f"{tick_mark}")

    print("Dumping code to strava_tokens.json file...", end=" ")
    with open(f'{path}/strava_tokens.json', 'w') as outfile:
        json.dump(json_result.json(), outfile)
    print(f"{tick_mark}")

### UTILITY FUNCTIONS
if __name__ == '__main__':
    # read client id and secret from config file and get latest access token
    # this is very quick so it's not detrimental to do it each time the code is ran
    client_id = read_config('client_id')
    client_secret = read_config('client_secret')
    access_token = get_access_token(client_id, client_secret)

    # create the dataframe of run activities
    df_path = f"{os.path.dirname(os.path.realpath(__file__))}/activities.csv"
    if input("Re-create dataframe? (y/n) ") == "y":
        df = fetch_dataframe()
        df.to_csv(df_path)
    else:
        df = pd.read_csv(df_path)

    args = extract_run_data(df)

    # allow the user to choose plots
    print("\nPlot choices")
    print("-----------")

    all_plots = True if input("Plot all? (y/n) ") == "y" else False
    plot_choices = (True, )*7
    if not all_plots:
        dist = True if input("Plot distances? (y/n) ") == "y" else False
        pace = True if input("Plot paces? (y/n) ") == "y" else False
        hr = True if input("Plot heart rates? (y/n) ") == "y" else False
        cad = True if input("Plot cadences? (y/n) ") == "y" else False
        weekly_dist = True if input("Plot weekly distance totals? (y/n) ") == "y" else False
        hr_vs_pace = True if input("Plot heart rate vs pace? (y/n) ") == "y" else False
        cad_vs_pace = True if input("Plot cadence vs pace? (y/n) ") == "y" else False

        plot_choices = (dist, pace, hr, cad, weekly_dist, hr_vs_pace, cad_vs_pace)

    plot_all(*args, plot_choices=plot_choices)
