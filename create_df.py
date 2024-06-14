import os
import json
import requests
import pandas as pd
import numpy as np
import utils

tick_mark = "\u2714"

def fetch_dataframe():
    """ Get dataframe of activities from Strava API"""
    print("\nFetch Dataframe of activities")
    print("------------------------------")

    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    print("Getting token data from strava_tokens.json file...", end=" ")
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/strava_tokens.json') as f:
        token_data = json.load(f)
    print(f"{tick_mark}")

    print("Getting all activities and creating dataframe...")
    header = {'Authorization': 'Bearer ' + token_data['access_token']}
    per_page = 50
    page = 1
    
    # this line gets the first page of data
    df = requests.get(activites_url, headers=header, params={'per_page': per_page, 'page': page}).json()

    # this while loop gets subsequent pages, until we hit the last result
    while True:
        page += 1
        temp_df = requests.get(activites_url, headers=header, params={'per_page': per_page, 'page': page}).json()
        if not temp_df:
            break
        df += temp_df
    print(f"{tick_mark}")

    df = pd.json_normalize(df)

    return df

def extract_run_data(df):
    """ Extract only run data for all included metrics (e.g., distance, heart rate, pace, etc)"""
    print("\nExtract run data from dataframe")
    print("-----------------------------")

    # drop the dataframe rows that aren't runs
    df = df.drop(df[df['type'] != 'Run'].index)

    print("Getting run data from dataframe...", end=" ")
    distances = df['distance'] / 1000
    paces = 1 / (0.06 * df['average_speed']) # convert from m/s to mins/km
    av_hr = df['average_heartrate']
    cadences = 2 * df['average_cadence'] # multiply by two because the data is for only one leg
    dates = pd.to_datetime(df['start_date'], format='%Y-%m-%dT%H:%M:%SZ')
    total_runs = len(dates)

    date_range = pd.date_range(dates.iloc[-1], dates.iloc[0])

    null_data = np.zeros(shape=len(date_range)) - 1

    # get weekly average of data
    distances_weekly = utils.get_weekly_averaged_data(distances, dates)

    print(f"{tick_mark}")

    return f'{os.path.dirname(os.path.realpath(__file__))}/plots', dates, date_range, null_data, distances, paces, av_hr, cadences, total_runs, distances_weekly
