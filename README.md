# Plot data from runs using Strava's API
See plot examples [here](README.md#plot-examples)

## Set up
1. Firstly, follow the steps outline in step B here: https://developers.strava.com/docs/getting-started/. This will give you access to both your 'Client ID' and 'Client Secret', which are both necessary for using the API.
2. Clone this repository and make sure you Python environment has the required packages installed, listed in requirements.txt.
3. Enter the ID and secret values gained in step 1 into the 'config.txt' file, without quotation marks around the values:
```plaintext
client_id = 111111
client_secret = aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
```

## Using the tool
Run strava_data.py - in the command line you will be asked if you would like to create the dataframe (store the run data in activities.csv) and which plots to generate. Plot options are:
- Distances
- Average paces
- Average heart rates
- Average cadences (steps per min)
- Weekly distance (cumulative total of run distances for each week)
- Average heart rate vs average pace (example shown at the top of this README)
- Average cadence vs average pace

NOTE: you may have to change the bounds of each graph to fit with your data. All the relevant values are the arguments `ymin, ymax, ytick1, ytick2, tick_delta, h_line_loc` defined in `plot_data.py`'s `create_plot` function

## Plot examples
![hr_vs_pace](https://github.com/Henryp1997/strava_plotting/assets/118852495/b3b4bc99-7941-4a7e-b1d7-ef5cd200421e)
![cadence_vs_pace](https://github.com/Henryp1997/strava_plotting/assets/118852495/c2755562-e556-49df-bbc0-dc208ca4731f)
