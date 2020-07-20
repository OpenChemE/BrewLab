# BrewLab

Original Author: Thanos Kritharis

This program communicates with 3 Arduino Megas for the purpose of gathering 
temperature, PH, and DO data from a batch fermenation process

The data is plotted in real time and collected in array where it is saved into
an automatically generated excel document

The program can also change temperature set-points within the fermenter through the usage
of pumps attached to the fermenters

## Development

1. Create a new virtual environment: `virtualenv --python=`which python3` env`
2. Activate the virtual environment: source env/bin/activate
3. Install the package in development mode: `python setup.py develop`

If you don't have an Arduino to connect to for testing set enviroment variable **MODE** to "dev".

## Usage

Run the program and select the fermenters you want to use by clicking the toggle buttons. Use the sliders to set the temperature setpoint for each fermenter.

Once in the Graphing screen, click "Start" to begin collecting data for the desired fermenters. Click a time range of data to view, and click a fermenter to select which fermenter you would like to view. 

In the Config page, you can turn a pump between AUTO/MANUAL and when in MANUAL can turn the pump ON/OFF. To adjust the temperature setpoint after starting the program, slide the slider of the fermenter to the desired temperature and click "Back". 

## Future Work

For future development see Issues.