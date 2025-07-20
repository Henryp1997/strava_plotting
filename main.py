import json
import os
import sys
import requests
import urllib3
from typing import Literal
import pandas as pd

from utils import read_config
import create_df
from plot_data import plot_all

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

here = os.path.dirname(os.path.realpath(__file__))
tick_mark = "\u2714"


def main() -> None:
    """ Execute the program. Grab data using the Strava API and generate chosen plots """

    get = wait_for_input("Re-retrieve API access token?")
    if get == "y":
        # Read client id and secret from config file and get latest access token
        client_id = read_config("client_id")
        client_secret = read_config("client_secret")
        get_access_token(client_id, client_secret)

    # Create the dataframe of run activities
    df_path = f"{here}/activities.csv"  
    recreate = wait_for_input("Re-create dataframe?")
    if recreate == "y":
        json_header = load_token_data()
        df = create_df.fetch_dataframe(json_header)
        if df is None:
            sys.exit()
        df.to_csv(df_path)
    elif recreate == "n":
        df = pd.read_csv(df_path)

    run_data = create_df.extract_run_data_from_df(df)

    # Allow the user to choose plots
    print("\nPlot choices")
    print("-----------")

    all_plots = wait_for_input("Plot all?") == "y"
    plot_choices = (True, )*7
    if not all_plots:
        distance    = wait_for_input("Plot distances?") == "y"
        pace        = wait_for_input("Plot paces?") == "y"
        heartrate   = wait_for_input("Plot heart rates?") == "y"
        cadence     = wait_for_input("Plot cadences?") == "y"
        weekly_dist = wait_for_input("Plot weekly distance totals?") == "y"
        hr_vs_pace  = wait_for_input("Plot heart rate vs pace?") == "y"
        cad_vs_pace = wait_for_input("Plot cadence vs pace?") == "y"

        plot_choices = (distance, pace, heartrate, cadence, weekly_dist, hr_vs_pace, cad_vs_pace)

    plot_all(*run_data, plot_choices=plot_choices)


def get_access_token(
        client_id,
        client_secret,
        auth_url="https://www.strava.com/oauth/token"
    ) -> None:
    """ Request access token using client id, client secret and refresh token values """   
    payload = {
        "client_id"    : client_id,
        "client_secret": client_secret,
        "refresh_token": "55aa876957c95e4dbda77ed2a8572eb3d0101bff",
        "grant_type"   : "refresh_token",
        "f"            : "json"
    }
    print("Requesting token...", end=" ")
    json_result = requests.post(auth_url, data=payload, verify=False)
    print(f"{tick_mark}")

    print("Dumping token to 'strava_tokens.json'...", end=" ")
    with open(f"{here}/strava_tokens.json", "w") as outfile:
        json.dump(json_result.json(), outfile)
    print(f"{tick_mark}")


def load_token_data() -> dict:
    """ Load the API access token from JSON and package into a JSON header """
    print("Getting token data from strava_tokens.json file...", end=" ")
    with open(f"{here}/strava_tokens.json") as f:
        token_data = json.load(f)
    try:
        json_header = {"Authorization": f"Bearer {token_data['access_token']}"}
    except KeyError:
        # Access_token not found in JSON file
        print("\u2a2f\nAccess token not found. Have you added your Client ID and Client Secret to 'config.txt'?")
        return None

    print(f"{tick_mark}")
    return json_header


def wait_for_input(msg) -> Literal["y", "n"]:
    """ Wait for user to confirm or deny performing a certain action """
    perform_action = ""
    change_msg = False
    while perform_action not in ("y", "n"):
        input_msg = f"\n{msg} (y/n): " if not change_msg else 'Please enter "y" or "n": '
        perform_action = input(input_msg).lower()
        change_msg = True
    
    return perform_action


if __name__ == '__main__':
    main()
