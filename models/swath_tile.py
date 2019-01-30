import pandas as pd
import h5py as hdf
import pyhdf.SD as hdf
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import pyproj as proj
from operator import itemgetter
from shapely import geometry
from shapely.ops import cascaded_union
from shapely.ops import unary_union
from ..geoutils import geoutils as gu


class SwathTile:

    def __init__(self, datatype, geo_file_paths, data_file_paths):
        self.datatype = datatype
        self.geo_file_paths = geo_file_paths
        self.data_file_paths = data_file_paths

        #TODO: Extract timestamp from time of data collection
        self.timestamps = [dt.datetime.now()]
        self.in_projection = proj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
        self.out_projection = proj.Proj(init='epsg:3857')

    def __calculate_bounds__(self, project, latitude_dataframe, longitude_dataframe):
        shape = latitude_dataframe.shape

        x_length = shape[0]
        y_length = shape[1]

        points = []
        points.extend(self.__get_edge__(y_length, 0, True, project, longitude_dataframe, latitude_dataframe))
        points.extend(self.__get_edge__(y_length, -1, True, project, longitude_dataframe,latitude_dataframe))
        points.extend(self.__get_edge__(x_length, 0, False, project, longitude_dataframe, latitude_dataframe))
        points.extend(self.__get_edge__(x_length, -1, False, project, longitude_dataframe, latitude_dataframe))

        points = gu.sort_coordinates(points)

        bounding_poly = geometry.Polygon(points)
        return bounding_poly

    def merge(self, other):
        self.geo_file_paths.extend(other.geo_file_paths)
        self.data_file_paths.extend(other.data_file_paths)
        self.bounds = cascaded_union([self.bounds, other.bounds]).buffer(2).buffer(-2)
        self.real_bounds = cascaded_union([self.real_bounds, other.real_bounds]).buffer(2).buffer(-2)
        self.timestamps.extend(other.timestamps)
        return self

    def plot(self):
        x,y = self.bounds.exterior.xy
        plt.scatter(x, y)
        plt.show()

    def __get_edge__(self, length, ordinal, side, project, longitude_dataframe, latitude_dataframe):
        points = []

        for i in range(0, length - 1):
            if side:
                lat = latitude_dataframe.iloc[ordinal, i]
                lon = longitude_dataframe.iloc[ordinal, i]
            else:
                lat = latitude_dataframe.iloc[i, ordinal]
                lon = longitude_dataframe.iloc[i, ordinal]

            point = (lon, lat)
            points.append(point)

        points = [self.__project__(point[0], point[1]) for point in points]
        return points

    def __project__(self, x, y):
        x2 = x
        y2 = y
        if x < 0:
            x2 = x + 360
        return (x2,y2)

    def __get_variable_dataframe__(self):
        raise NotImplementedError()

    def __get_geo_dataframe__(self, coord_type):
        raise NotImplementedError()


