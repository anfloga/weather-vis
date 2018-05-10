from flask import Flask
from flask import request
app = Flask(__name__)

import data_manager as dm
import os
import pandas as pd
import threading
import json

swath_manager = dm.SwathTileManager()
test_box = dm.BoundingBox({'lat':67.0,'long':-102.0},{'lat':67.0,'long':-100.0},{'lat':65.0,'long':-102.0},{'lat':65.0,'long':-100.0})


@app.route("/query",methods=['POST'])
def query():
    corners = request.get_json()["corners"]
    query_box = dm.BoundingBox(corners[0],corners[1],corners[2],corners[3])
    query_box.print_geometries()
    return swath_manager.query_tiles("Cloud_Top_Height", query_box).to_csv()

@app.route("/geom")
def geoms():
    geoms = []
    for tile in swath_manager.swath_tile_list:
        geoms.append(tile.bounding_box.print_geometries())
    return "view terminal for bounds"
