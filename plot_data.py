import os
import math

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from scipy.optimize import curve_fit

plt.rcParams["axes.facecolor"] = "#FFFFFF"
plt.rcParams["figure.dpi"] = 300
plt.rcParams["figure.figsize"] = (11, 5)
tick_mark = "\u2714"

data_vs_date_args = {
    "distance":{
        "units" : "km",
        "ylims" : (0, 25),
        "yticks": (0, 25, 2.5),
        "h_line": 5
    },
    "pace": {
        "units" : "mins/km",
        "ylims" : (4.5, 7.5),
        "yticks": (4.5, 7.5, 0.5),
        "h_line": 5
    },
    "heartrate": {
        "units" : "bpm",
        "ylims" : (130, 190),
        "yticks": (130, 190, 10),
        "h_line": -1
    },
    "cadence": {
        "units" : "steps/min",
        "ylims" : (140, 185),
        "yticks": (140, 185, 5),
        "h_line": 180
    }
}

def plot_versus_date(name, total_runs, plot_filepath, date_range, dates, null_data, ydata):
    """ General function for plotting running data against datetime """
    _, ax = plt.subplots(figsize=(11, 5), dpi=150, facecolor="#FFFFFF")
    args = data_vs_date_args[name]
    ymin, ymax = args["ylims"]
    ax.axis(ymin=ymin)
    ax.axis(ymax=ymax)

    ax.grid(linewidth=0.5)

    ytick1, ytick2, tick_delta = args["yticks"]
    ax.set_yticks(np.arange(ytick1, ytick2, tick_delta))
    ax.set_ylabel(f"{name.capitalize()} ({units})")
    ax.set_xlabel("Date", labelpad=10)

    units = args["units"]
    ax.set_title(f"Running {name} in {units} ({total_runs} runs)")

    h_line_loc = args["h_line"]
    ax.axhline(h_line_loc, color="k", linestyle="--")
    if name == "distance":
        ax.axhline(h_line_loc + 5, color="k", linestyle="--")

    ax.plot(date_range, null_data)
    ax.plot(dates, ydata, "-bo", mec="#000", mfc="#727ffc")
    plt.savefig(f"{plot_filepath}/{name}_vs_date.svg")
    plt.savefig(f"{plot_filepath}/{name}_vs_date.png")


def plot_all(
    dates,
    date_range,
    null_data,
    distances,
    paces,
    av_HR,
    cadences,
    total_runs,
    distances_weekly,
    plot_choices=(),
    plot_filepath=f"{os.path.dirname(os.path.realpath(__file__))}/plots"
):
    print("\nPlotting")
    print("-----------")

    dist, pace, hr, cad, weekly_dist, hr_vs_pace, cad_vs_pace = plot_choices

    ### First four plots have the same args (all are data versus date)
    all_data = {
        "distance": dist, "pace": pace, "heartrate": hr, "cadence": cad
    }
    for i, name in enumerate(("distance", "pace", "heartrate", "cadence")):
        if plot_choices[i]:
            # Only plot if user chose to do so
            print(f"Plotting {name}...", end=" ")
            plot_versus_date(name, total_runs, plot_filepath, date_range, dates, null_data, all_data[name])
            print(f"{tick_mark}")

    ### Remaining plots are dissimilar
    # Weekly distance plot
    if weekly_dist:
        print("Plotting weekly distances...", end=" ")
        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor="#FFFFFF")
        ax.grid(linewidth=0.5)
        ax.set_ylabel("Weekly distance (km)", labelpad=10)
        ax.set_xlabel("Week number")
        ax.set_title("Weekly distance")
        ax.set_xticks(np.arange(0,len(distances_weekly),5))

        ax.plot(distances_weekly, "-bo", mec="#000", mfc="#727ffc")
        plt.savefig(f"{plot_filepath}/weekly_distance.svg")
        plt.savefig(f"{plot_filepath}/weekly_distance.png")
        print(f"{tick_mark}")

    # Pace vs average HR
    if hr_vs_pace:
        print("Plotting heart rate vs pace...", end=" ")

        # Remove nans from heart rate (run before optical sensor watch)
        new_paces = []
        new_HR = []
        new_distances = []

        paces = list(paces)
        distances = list(distances)

        for i, val in enumerate(av_HR):
            if not math.isnan(val):
                new_paces.append(paces[i])
                new_HR.append(val)
                new_distances.append(distances[i])

        fig, ax = plt.subplots(figsize=(11,5), dpi=150, facecolor="#FFFFFF")
        ax.axis(ymin=130)
        ax.axis(ymax=190)

        ax.grid(linewidth=0.5)

        ax.set_yticks(np.arange(130, 190, 10))
        ax.set_ylabel("HR (bpm)")
        ax.set_xlabel("Pace (mins/km)", labelpad=10)
        ax.set_title(f"Average HR vs pace")

        scatter = ax.scatter(new_paces, new_HR, c=new_distances, cmap="cividis")

        divider = make_axes_locatable(ax)
        cax = divider.append_axes("right", size="5%", pad=0.05)

        cbar = fig.colorbar(scatter, cax=cax, orientation="vertical")
        cbar.ax.set_ylabel("Distance (km)")

        # Fit best line to data
        popt, _ = curve_fit(lambda x, m, c: m*x + c, new_paces, new_HR)
        
        x_fit = np.linspace(4.3, 7.5, 1000)
        ax.plot(x_fit, popt[0]*x_fit + popt[1], "b--")

        plt.savefig(f"{plot_filepath}/hr_vs_pace.svg")
        plt.savefig(f"{plot_filepath}/hr_vs_pace.png")
        print(f"{tick_mark}")

    # Pace vs cadence
    if cad_vs_pace:
        print("Plotting cadence vs pace...", end=" ")
        fig, ax = plt.subplots(figsize=(11, 5), dpi=150, facecolor="#FFFFFF")
        # ax.axis(ymin=130)
        # ax.axis(ymax=190)

        ax.grid(linewidth=0.5)

        # ax.set_yticks(np.arange(130,190,10))
        ax.set_ylabel("Cadence (steps/min)")
        ax.set_xlabel("Pace (mins/km)", labelpad=10)
        ax.set_title(f"Average cadence vs pace")
        
        # Remove nans from heart rate (run before optical sensor watch)
        new_paces = []
        new_cadences = []

        paces = list(paces)

        for i, val in enumerate(cadences):
            if not math.isnan(val):
                new_paces.append(paces[i])
                new_cadences.append(val)

        # Fit best line to data
        popt, _ = curve_fit(lambda x, m, c: m*x + c, new_paces, new_cadences)
        
        x_fit = np.linspace(4.3, 7.5, 1000)
        ax.plot(x_fit, popt[0]*x_fit + popt[1], "b--")

        ax.plot(paces, cadences, "bo", mec="#000", mfc="#727ffc")
        plt.savefig(f"{plot_filepath}/cadence_vs_pace.svg")
        plt.savefig(f"{plot_filepath}/cadence_vs_pace.png")
        print(f"{tick_mark}")
