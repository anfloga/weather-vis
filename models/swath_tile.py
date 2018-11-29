import pandas as pd
import h5py as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from ..geoutils import geoutils as gu

class SwathTile:

    def __init__(self, geo_file_path, data_file_path):
        self.geo_file_path = geo_file_path
        self.data_file_path = data_file_path

        geo_data_file = hdf.File(geo_file_path)
        long_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Longitude'][:])
        lat_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Latitude'][:])

        self.bounds = self.__calculate_bounds__(lat_data, long_data)
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

