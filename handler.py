from flask import Flask
from flask import request
from flask import send_from_directory
app = Flask(__name__)

import os
import pandas as pd

import threading
import json
from .models.query import Query
from .models.layer import Layer
from .services.viirs_service import ViirsService
from .services.modis_service import ModisService
from shapely.geometry import shape, Point, mapping, Polygon


base_data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/test/cbh")
geo_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/test/geo")
top_data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/test/cth")
modis_directory = os.fsencode("/media/joe/DATA/weather_data/raw/201810319")

#base_service = ViirsService('base', geo_directory, base_data_directory)
top_service = ViirsService('AverageCloudTopHeight', 'VIIRS-CTH-EDR_All', z_scale = 200000, geo_directory = geo_directory, data_directory = top_data_directory)
#top_service = ModisService('Cloud_Top_Height', '', z_scale = 10, geo_directory = modis_directory, data_directory = modis_directory)

top = Layer("")

@app.route("/")
def root():
    return app.send_static_file("home.html")

@app.route("/query",methods=['POST'])
def query():
    body = request.get_json()

    features = body['features']

    if len(features) > 1:
        return "only 1 feature allowed"

    query = Query(request)
    top.layer_json = top_service.query(query)
    return "success"

@app.route("/layer")
def get():

    layer_name = request.args.get('name')

    if layer_name == 'base':
        return base
    if layer_name == 'top':
        return top.layer_json

