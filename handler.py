from flask import Flask
from flask import request
from flask import send_from_directory
app = Flask(__name__)

import data_manager as dm
import os
import pandas as pd
import geoutils as gu
import threading
import json



base_data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/cbh")
geo_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/geo")
top_data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/cth")

base_swath_manager = dm.SwathTileManager(base_data_directory, geo_directory)
top_swath_manager = dm.SwathTileManager(top_data_directory, geo_directory)
test_box = dm.BoundingBox({'lat':67.0,'long':-102.0},{'lat':67.0,'long':-100.0},{'lat':65.0,'long':-102.0},{'lat':65.0,'long':-100.0})

@app.route("/")
def root():
    return app.send_static_file("home.html")

@app.route("/query",methods=['POST'])
def query():
    corners = request.get_json()["corners"]
    debug = request.get_json()["debug"]
    corners = gu.sort_coordinates(corners)
    query_box = dm.BoundingBox(corners[0],corners[1],corners[2],corners[3], debug)
    query_box.print_geometries()
    base_geometry = base_swath_manager.query_tiles("VIIRS-CBH-EDR_All", "AverageCloudBaseHeight", query_box)
    base_swath_manager.set_current_geometry(base_geometry)
    base_swath_manager.build_layer_map("AverageCloudBaseHeight", query_box)
    top_geometry = top_swath_manager.query_tiles("VIIRS-CTH-EDR_All", "AverageCloudTopHeight", query_box)
    top_swath_manager.set_current_geometry(top_geometry)
    top_swath_manager.build_layer_map("AverageCloudTopHeight", query_box)

    return "success"

@app.route("/layer")
def get():

    layer_name = request.args.get('name')

    if layer_name == 'base':
        return base_swath_manager.layer
    if layer_name == 'top':
        return top_swath_manager.layer

@app.route("/geom")
def geoms():
    geoms = []
    for tile in swath_manager.swath_tile_list:
        geoms.append(tile.bounding_box.print_geometries())
    return "view terminal for bounds"

#data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/cbh")
#geo_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/geo")

