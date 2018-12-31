import pandas as pd
import h5py as hdf
import pyhdf.SD as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from shapely.ops import cascaded_union
from ..geoutils import geoutils as gu


class SwathTile:

    def __init__(self, datatype, geo_file_paths, data_file_paths):
        self.datatype = datatype
        self.geo_file_paths = geo_file_paths
        self.data_file_paths = data_file_paths
        self.timestamp = dt.datetime.now()

    def __calculate_bounds__(self, latitude_dataframe, longitude_dataframe):
        shape = latitude_dataframe.shape

        x_length = shape[0]
        y_length = shape[1]

        points = []
        points.extend(self.__get_edge__(y_length, 0, True, longitude_dataframe, latitude_dataframe))
        points.extend(self.__get_edge__(y_length, -1, True, longitude_dataframe,latitude_dataframe))
        points.extend(self.__get_edge__(x_length, 0, False, longitude_dataframe, latitude_dataframe))
        points.extend(self.__get_edge__(x_length, -1, False, longitude_dataframe, latitude_dataframe))

        points = gu.sort_coordinates(points)

        bounding_poly = geometry.Polygon(points)
        return bounding_poly

    def merge(self, other):
        self.geo_file_paths.extend(other.geo_file_paths)
        self.data_file_paths.extend(other.geo_file_paths)
        self.bounds = cascaded_union([self.bounds, other.bounds])
        self.plot()

    def plot(self):
        x,y = self.bounds.exterior.xy
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(x, y, color='#6699cc', alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)
        ax.set_title('Polygon')
        plt.show()

    def __get_edge__(self, length, ordinal, side, longitude_dataframe, latitude_dataframe):
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

        return points

    def __get_variable_dataframe__(self):
        raise NotImplementedError()

    def __get_geo_dataframe__(self, coord_type):
        raise NotImplementedError()


