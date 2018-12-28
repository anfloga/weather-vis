import pandas as pd
import pyhdf.SD as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from .swath_tile import SwathTile
from ..geoutils import geoutils as gu


class ModisTile(SwathTile):

    def __init__(self, datatype, geo_file_path, data_file_path):
        super().__init__(datatype, geo_file_path, data_file_path)

        geo_data_file = hdf.SD(geo_file_path, hdf.SDC.READ)
        long_data = pd.DataFrame(geo_data_file.select('Longitude').get())
        lat_data = pd.DataFrame(geo_data_file.select('Latitude').get())

        self.bounds = self.__calculate_bounds__(lat_data, long_data)

    def __get_variable_dataframe__(self, tile):
        variable_data = pd.DataFrame(hdf.SD(tile.data_file_path, hdf.SDC.READ).select(self.datatype).get())
        return variable_data

    def __get_geo_dataframe__(self, tile, coord_type):
        coord_data = pd.DataFrame(hdf.SD(tile.geo_file_path, hdf.SDC.READ).select(coord_type).get())
        return coord_data


