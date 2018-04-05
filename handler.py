from flask import Flask
app = Flask(__name__)

import data_fetcher as ft
import data_manager as dm
import os
import pandas as pd
import threading


swath_manager = dm.SwathTileManager()
data_fetcher = ft.DataFetcher()


def update():
    threading.Timer(3.0, update).start()
    data_fetcher.download_latest_file()
    print('test')

update()


@app.route("/")
def handler():
    directory = os.fsencode("/media/joe/DATA/weather_data/raw/")
    test_box = dm.BoundingBox({'lat':-34.0,'long':145.0},{'lat':-34.0,'long':148.0},{'lat':-38.0,'long':145.0},{'lat':-38.0,'long':149.0})
    for file in os.listdir(directory):
        filename = os.fsdecode(directory) + os.fsdecode(file)
        swath_manager.build_swath_tile(filename)
    return swath_manager.get_merged_swath_dataframe("Cloud_Top_Height",test_box).to_json(orient='records')

