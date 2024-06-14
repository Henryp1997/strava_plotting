import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.optimize import curve_fit
import math
import numpy as np

plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['figure.dpi'] = 300
plt.rcParams["figure.figsize"] = (11, 5)
tick_mark = "\u2714"

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

def plot_all(plot_filepath, dates, date_range, null_data, distances, paces, av_HR, cadences, total_runs, distances_weekly, plot_choices=()):
    print("\nPlotting")
    print("-----------")

    dist, pace, hr, cad, weekly_dist, hr_vs_pace, cad_vs_pace = plot_choices

    if dist:
        print("Plotting distances...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, distances, 'distance', f"Running distance in kilometers since April 2022 ({total_runs} runs)", "Distance (km)", 0, 25, 0, 25, 2.5, 5)
        print(f"{tick_mark}")

    if pace:
        print("Plotting paces...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, paces, 'pace', f"Running pace in minutes per kilometer since April 2022 ({total_runs} runs)", "Pace (mins/km)", 4.5, 7.5, 4.5, 7.5, 0.5, 5)
        print(f"{tick_mark}")

    if hr:
        print("Plotting heart rates...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, av_HR, 'heartrate', f"Heartrate in bpm since April 2022 ({total_runs} runs)",'HR (bpm)', 130, 190, 130, 190, 10, -1)
        print(f"{tick_mark}")

    if cad:
        print("Plotting cadences...", end=" ")
        create_plot(plot_filepath, date_range, dates, null_data, cadences, 'cadences', f"Cadence in steps per minute since April 2022 ({total_runs} runs)", "Cadence (spm)", 140, 185, 140, 185, 5, 180)
        print(f"{tick_mark}")

    # weekly distance plot
    if weekly_dist:
        print("Plotting weekly distances...", end=" ")
        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
        ax.grid(linewidth=0.5)
        ax.set_ylabel('Weekly distance (km)', labelpad=10)
        ax.set_xlabel('Week number')
        ax.set_title('Weekly distance')
        ax.set_xticks(np.arange(0,len(distances_weekly),5))

        ax.plot(distances_weekly, "-bo", mec='#000', mfc='#727ffc')
        plt.savefig(f'{plot_filepath}/weekly_distance.svg')
        plt.savefig(f'{plot_filepath}/weekly_distance.png')
        print(f"{tick_mark}")

    # pace vs average HR
    if hr_vs_pace:
        print("Plotting heart rate vs pace...", end=" ")

        # remove nans from heart rate (run before optical sensor watch)
        new_paces = []
        new_HR = []
        new_distances = []

        # not sure why these need to be converted to lists, but I was
        # getting KeyErrors in the loop below before converting them
        paces = list(paces)
        distances = list(distances)

        for i, val in enumerate(av_HR):
            if not math.isnan(val):
                new_paces.append(paces[i])
                new_HR.append(val)
                new_distances.append(distances[i])

        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor='#FFFFFF')
        ax.axis(ymin=130)
        ax.axis(ymax=190)

        ax.grid(linewidth=0.5)

        ax.set_yticks(np.arange(130, 190, 10))
        ax.set_ylabel('HR (bpm)')
        ax.set_xlabel("Pace (mins/km)", labelpad=10)
        ax.set_title(f'Average HR vs pace')

        scatter = ax.scatter(new_paces, new_HR, c=new_distances, cmap="cividis")

        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='5%', pad=0.05)

        cbar = fig.colorbar(scatter, cax=cax, orientation="vertical")
        cbar.ax.set_ylabel("Distance (km)")

        # fit best line to data
        popt, pcov = curve_fit(lambda x, m, c: m*x + c, new_paces, new_HR)
        
        x_fit = np.linspace(4.3, 7.5, 1000)
        ax.plot(x_fit, popt[0]*x_fit + popt[1], "b--")

        plt.savefig(f'{plot_filepath}/hr_vs_pace.svg')
        plt.savefig(f'{plot_filepath}/hr_vs_pace.png')
        print(f"{tick_mark}")

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
        print(f"{tick_mark}")