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

swath_manager = dm.SwathTileManager()
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
    geometry = swath_manager.query_tiles("Cloud_Top_Height", query_box)
    swath_manager.set_current_geometry(geometry)
    swath_manager.build_layer_map(query_box)
    return "success"

@app.route("/get")
def get():
    return swath_manager.layer

@app.route("/geom")
def geoms():
    geoms = []
    for tile in swath_manager.swath_tile_list:
        geoms.append(tile.bounding_box.print_geometries())
    return "view terminal for bounds"
