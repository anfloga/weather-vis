from flask import Flask
app = Flask(__name__)

import data_manager2 as dm
import os
import pandas as pd
import threading


swath_manager = dm.SwathTileManager()
test_box = dm.BoundingBox({'lat':67.0,'long':-102.0},{'lat':67.0,'long':-100.0},{'lat':65.0,'long':-102.0},{'lat':65.0,'long':-100.0})


@app.route("/")
def handler():
    return swath_manager.get_merged_swath_dataframe("Cloud_Top_Height",test_box).to_json(orient='records')


@app.route("/trigger")
def trigger():
    directory = os.fsencode("/media/joe/DATA/weather_data/raw/201811322")
    for file in os.listdir(directory):
        filename = os.fsdecode(directory) + "/" + os.fsdecode(file)
        print(filename)
        tile = dm.SwathTile(filename)
        if swath_manager.tile_in_bound(tile, test_box):
            swath_manager.add_tile_to_list(tile)

    return "done"

