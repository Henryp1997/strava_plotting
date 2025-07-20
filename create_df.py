import requests
import pandas as pd
import numpy as np
import utils

tick_mark = "\u2714"

desired_columns = [
    "distance",
    "average_speed",
    "average_heartrate",
    "average_cadence",
    "start_date",
]

def fetch_dataframe(
        json_header,
        activities_url="https://www.strava.com/api/v3/athlete/activities",
        per_page=100,
        page=1
    ):
    """ Get dataframe of activities from Strava API"""
    print("\nFetch Dataframe of activities")
    print("------------------------------")

    # Get the first page of data
    params = {
        "per_page": per_page,
        "page": page
    }
    data = requests.get(activities_url, headers=json_header, params=params).json()
    if isinstance(data, dict):
        # If access token is invalid, 'data' is only a single dictionary containing the errors
        if data["message"] == "Authorization Error":
            error = "Access code invalid/expired! Please try regenerating the access token."
        elif data["message"] == "Bad Request":
            error = f"'Bad Request' received. Try reducing the value of 'per_page' (current = {per_page})"
        else:
            error = f"Unknown error occurred when requesting data. Error message is {data['message']}"
        raise RuntimeError(error)

    # Get subsequent pages until we hit the last result
    print(f"Getting {per_page} activities per page")
    while True:
        print(f"Page {page}...", end=" ")
        page += 1
        params["page"] = page
        temp_data = requests.get(activities_url, headers=json_header, params=params).json()
        if not temp_data:
            break
        data += temp_data
        print(f"{tick_mark}")
    print("All activities loaded!")

    df = pd.json_normalize(data) # Convert to Pandas DataFrame

    # Drop the dataframe rows that aren't runs
    df = df.drop(df[df["type"] != "Run"].index)

    # Drop the undesired dataframe columns
    undesired_columns = set(df.columns) - set(desired_columns)
    df = df.drop(columns=list(undesired_columns))

    return df


def extract_run_data_from_df(df):
    """ Extract only run data for all included metrics (e.g., distance, heart rate, pace, etc) """
    print("\nExtract run data from dataframe")
    print("-----------------------------")
    print("Getting run data from dataframe...", end=" ")
    distances = df["distance"] / 1000
    paces = 1 / (0.06 * df["average_speed"]) # Convert from m/s to mins/km
    av_hr = df["average_heartrate"]
    cadences = 2 * df["average_cadence"] # Multiply by two because the data is for only one leg
    dates = pd.to_datetime(df["start_date"], format="%Y-%m-%dT%H:%M:%SZ")
    total_runs = len(dates)

    date_range = pd.date_range(dates.iloc[-1], dates.iloc[0])

    null_data = np.zeros(shape=len(date_range)) - 1

    # Get weekly average of data
    distances_weekly = utils.get_weekly_averaged_data(distances, dates)

    print(f"{tick_mark}")

    return dates, date_range, null_data, distances, paces, av_hr, cadences, total_runs, distances_weekly
