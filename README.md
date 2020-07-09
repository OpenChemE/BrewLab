# BrewLab

Original Author: Thanos Kritharis

This program communicates with 3 Arduino Megas for the purpose of gathering 
temperature, PH, and DO data from a batch fermenation process

The data is plotted in real time and collected in array where it is saved into
an automatically generated excel document

The program can also change temperature set-points within the fermenter through the usage
of pumps attached to the fermenters

## Setup

1. Create a new virtual environment: `virtualenv --python=`which python3` env`
2. Activate the virtual environment: source env/bin/activate
3. Install the package in development mode: `python setup.py develop`