import json
import os
import requests
import urllib3
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from datetime import datetime

import utils

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['figure.dpi'] = 300
plt.rcParams["figure.figsize"] = (11,5)

def get_token():

    print("\nAuthorise API access")
    print("--------------------")

    path = os.path.dirname(os.path.realpath(__file__))
    client_id = read_config('client_id')
    client_secret = read_config('client_secret')
    redirect_uri = 'http://localhost/'

    # Authorization URL
    request_url = f'http://www.strava.com/oauth/authorize?client_id={client_id}' \
                    f'&response_type=code&redirect_uri={redirect_uri}' \
                    f'&approval_prompt=force' \
                    f'&scope=profile:read_all,activity:read_all'

    profile = webdriver.FirefoxProfile(read_config("profile_path"))
    firefoxOptions = Options()
    firefoxOptions.profile = profile
    # firefoxOptions.headless = True
    firefoxOptions.binary_location = read_config("firefox_path")
    service = Service(executable_path=f"{path}/drivers/geckodriver.exe")
    browser = webdriver.Firefox(service=service, options=firefoxOptions)

    print("Opening firefox instance...", end=" ")
    browser.get(request_url)
    print("\u2714")

    # wait for facebook sign in button to load then click
    print("Logging in with Facebook...", end=" ")
    element_present = EC.presence_of_element_located((By.XPATH, '/html/body/div[2]/div[2]/div/form/div[1]/a'))
    WebDriverWait(browser, 10).until(element_present)
    browser.execute_script('arguments[0].click()', browser.find_element(By.XPATH, '/html/body/div[2]/div[2]/div/form/div[1]/a'))
    print("\u2714")

    # wait for strava authorize button to load then click
    print("Authorising API access...", end=" ")
    element_present = EC.presence_of_element_located((By.ID, 'authorize'))
    WebDriverWait(browser, 10).until(element_present)
    browser.execute_script('arguments[0].click()', browser.find_element(By.ID, 'authorize'))
    print("\u2714")

    # wait for 'Try again' button to appear which indicates that the page with url containing code has loaded
    print("Getting access code...", end=" ")
    element_present = EC.presence_of_element_located((By.ID, 'neterrorTryAgainButton'))
    WebDriverWait(browser, 10).until(element_present)
    print("\u2714")

    # grab auth code from url
    code = browser.current_url.split("code=")[1].split("&")[0]

    # get the access token
    token = requests.post(verify=False, url='https://www.strava.com/api/v3/oauth/token',
                        data={'client_id': client_id,
                              'client_secret': client_secret,
                              'code': code,
                              'grant_type': 'authorization_code'})

    # save json response as a variable
    strava_token = token.json()

    print("Dumping code to strava_tokens.json file...", end=" ")
    with open(f'{path}/strava_tokens.json', 'w') as outfile:
        json.dump(strava_token, outfile)
    print("\u2714")

    browser.close()

def create_dataframe():

    print("\nCreate Dataframe of activities")
    print("------------------------------")

    # auth_url = "https://www.strava.com/oauth/token"
    activites_url = "https://www.strava.com/api/v3/athlete/activities"

    print("Getting token data from strava_tokens.json file...", end=" ")
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/strava_tokens.json') as f:
        token_data = json.load(f)
    print("\u2714")

    print("Getting all activities and creating dataframe...")
    header = {'Authorization': 'Bearer ' + token_data['access_token']}
    per_page = 50
    page = 1
    df = requests.get(activites_url, headers=header, params={'per_page': per_page, 'page': page}).json()
    while True:
        page += 1
        temp_df = requests.get(activites_url, headers=header, params={'per_page': per_page, 'page': page}).json()
        if not temp_df:
            break
        df += temp_df
    
    print("\u2714")

    df = pd.json_normalize(df)

    print("Extracting data from dataframe...", end=" ")
    distances = [j/1000 for i, j in enumerate(df['distance']) if df['type'][i] == 'Run']

    paces = [(1/(0.06*j)) for i, j in enumerate(df['average_speed']) if df['type'][i] == 'Run']
    paces[-1] = 5.07

    kudos = [j for i, j in enumerate(df['kudos_count']) if df['type'][i] == 'Run']

    av_HR = [j for i, j in enumerate(df['average_heartrate']) if df['type'][i] == 'Run']

    cadences = [2*j for i, j in enumerate(df['average_cadence']) if df['type'][i] == 'Run']

    efforts = [j for i, j in enumerate(df['suffer_score']) if df['type'][i] == 'Run']

    dates = [j for i, j in enumerate(df['start_date']) if df['type'][i] == 'Run']
    dates = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%SZ') for i in dates]

    total_runs = len(dates)

    date_range = pd.date_range(dates[0], dates[-1])
    null_data = np.zeros(shape=len(date_range)) - 1

    # get weekly average of data
    dates_week = [j for i, j in enumerate(df['start_date']) if df['type'][i] == 'Run']
    dates_week = [datetime.strptime(i, '%Y-%m-%dT%H:%M:%SZ') for i in dates_week]
    distances_weekly = utils.get_weekly_averaged_data(distances, dates_week)

    print("\u2714")

    return f'{os.path.dirname(os.path.realpath(__file__))}/plots', dates, date_range, null_data, distances, paces, kudos, av_HR, cadences, efforts, total_runs, distances_weekly

def plot_all(plot_filepath, dates, date_range, null_data, distances, paces, kudos, av_HR, cadences, efforts, total_runs, distances_weekly, plot_choices=()):
    print("\nPlotting")
    print("-----------")

    dist, pace, kudos_, hr, cad, weekly_dist, hr_vs_pace, cad_vs_pace = plot_choices

    if dist:
        print("Plotting distances...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, distances, 'distance', f"Running distance in kilometers since April 2022 ({total_runs} runs)", "Distance (km)", 0, 25, 0, 25, 2.5, 5)
        print("\u2714")

    if pace:
        print("Plotting paces...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, paces, 'pace', f"Running pace in minutes per kilometer since April 2022 ({total_runs} runs)", "Pace (mins/km)", 4.5, 7.5, 4.5, 7.5, 0.5, 5)
        print("\u2714")

    if kudos_:
        print("Plotting kudos...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, kudos, 'kudos', f'Kudos over {total_runs} runs', 'Kudos count', 0, 5, 0, 5, 1, -1)
        print("\u2714")

    if hr:
        print("Plotting heart rates...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, av_HR, 'heartrate', f"Heartrate in bpm since April 2022 ({total_runs} runs)",'HR (bpm)', 130, 190, 130, 190, 10, -1)
        print("\u2714")

    if cad:
        print("Plotting cadences...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, cadences, 'cadences', f"Cadence in steps per minute since April 2022 ({total_runs} runs)", "Cadence (spm)", 140, 185, 140, 185, 5, 180)
        print("\u2714")

    # weekly distance plot
    if weekly_dist:
        print("Plotting weekly distances...", end=" ")
        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
        ax.grid(linewidth=0.5)
        ax.set_ylabel('Weekly distance (km)',labelpad=10)
        ax.set_xlabel('Week number')
        ax.set_title('Weekly distance')
        ax.set_xticks(np.arange(0,len(distances_weekly),5))

        ax.plot(distances_weekly, "-bo", mec='#000', mfc='#727ffc')
        plt.savefig(f'{plot_filepath}/weekly_distance.svg')
        plt.savefig(f'{plot_filepath}/weekly_distance.png')
        print("\u2714")

    # pace vs average HR
    if hr_vs_pace:
        print("Plotting heart rate vs pace...", end=" ")
        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
        ax.axis(ymin=130)
        ax.axis(ymax=190)

        ax.grid(linewidth=0.5)

        ax.set_yticks(np.arange(130, 190, 10))
        ax.set_ylabel('HR (bpm)')
        ax.set_xlabel("Pace (mins/km)",labelpad=10)
        ax.set_title(f'Average HR vs pace')
        # ax.axhline(h_line_loc,color='k',linestyle='--')
        # if filename == 'distance':
            # ax.axhline(h_line_loc+5,color='k',linestyle='--')

        ax.plot(paces, av_HR, "bo", mec='#000', mfc='#727ffc')
        plt.savefig(f'{plot_filepath}/hr_vs_pace.svg')
        plt.savefig(f'{plot_filepath}/hr_vs_pace.png')
        print("\u2714")

    # pace vs cadence
    if cad_vs_pace:
        print("Plotting cadence vs pace...", end=" ")
        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
        # ax.axis(ymin=130)
        # ax.axis(ymax=190)

        ax.grid(linewidth=0.5)

        # ax.set_yticks(np.arange(130,190,10))
        ax.set_ylabel('Cadence (steps/min)')
        ax.set_xlabel("Pace (mins/km)", labelpad=10)
        ax.set_title(f'Average cadence vs pace')
        # ax.axhline(h_line_loc,color='k',linestyle='--')
        # if filename == 'distance':
            # ax.axhline(h_line_loc+5,color='k',linestyle='--')

        ax.plot(paces, cadences, "bo", mec='#000', mfc='#727ffc')
        plt.savefig(f'{plot_filepath}/cadence_vs_pace.svg')
        plt.savefig(f'{plot_filepath}/cadence_vs_pace.png')
        print("\u2714")

### UTILITY FUNCTIONS
def read_config(string):
    with open(f'{os.path.dirname(os.path.realpath(__file__))}/config.txt', 'r') as f:
        params = f.readlines()
    
    return [i.split(" = ")[1] for i in params if string in i][0].strip("\n")

def create_plot(plot_filepath, date_range, dates, null_data, y_data, filename, title, ylabel, ymin, ymax, ytick1, ytick2, tick_delta, h_line_loc):
    fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
    ax.axis(ymin=ymin)
    ax.axis(ymax=ymax)

    ax.grid(linewidth=0.5)

    ax.set_yticks(np.arange(ytick1,ytick2,tick_delta))
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Date", labelpad=10)
    ax.set_title(title)
    ax.axhline(h_line_loc, color='k', linestyle='--')
    if filename == 'distance':
        ax.axhline(h_line_loc+5, color='k', linestyle='--')

    ax.plot(date_range, null_data)
    ax.plot(dates, y_data, "-bo", mec='#000', mfc='#727ffc')
    plt.savefig(f'{plot_filepath}/{filename}.svg')
    plt.savefig(f'{plot_filepath}/{filename}.png')

if __name__ == '__main__':
    if input("Authorise API access? (y/n) ") == "y":
        get_token()
    args = create_dataframe()

    print("\nPlot choices")
    print("-----------")
    dist = True if input("Plot distances? (y/n) ") == "y" else False
    pace = True if input("Plot paces? (y/n) ") == "y" else False
    kudos_ = True if input("Plot kudos? (y/n) ") == "y" else False
    hr = True if input("Plot heart rates? (y/n) ") == "y" else False
    cad = True if input("Plot cadences? (y/n) ") == "y" else False
    weekly_dist = True if input("Plot weekly distance totals? (y/n) ") == "y" else False
    hr_vs_pace = True if input("Plot heart rate vs pace? (y/n) ") == "y" else False
    cad_vs_pace = True if input("Plot cadence vs pace? (y/n) s") == "y" else False

    plot_choices = (dist, pace, kudos_, hr, cad, weekly_dist, hr_vs_pace, cad_vs_pace)
    plot_all(*args, plot_choices=plot_choices)
