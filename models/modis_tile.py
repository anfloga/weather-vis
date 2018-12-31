import pandas as pd
import pyhdf.SD as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from .swath_tile import SwathTile
from ..geoutils import geoutils as gu


class ModisTile(SwathTile):

    def __init__(self, datatype, geo_file_paths, data_file_paths):
        super().__init__(datatype, geo_file_paths, data_file_paths)

        geo_data_file = hdf.SD(geo_file_paths, hdf.SDC.READ)
        long_data = pd.DataFrame(geo_data_file.select('Longitude').get())
        lat_data = pd.DataFrame(geo_data_file.select('Latitude').get())

        self.bounds = self.__calculate_bounds__(lat_data, long_data)

    def __get_variable_dataframe__(self, tile):
        variable_data = pd.DataFrame(hdf.SD(self.data_file_paths[0], hdf.SDC.READ).select(self.datatype).get()).head(0)

        for path in self.data_file_paths:
            variable data = pd.concat([variable_data, pd.DataFrame(hdf.SD(path, hdf.SDC.READ).select(self.datatype).get())])

        return variable_data

    def __get_geo_dataframe__(self, tile, coord_type):

        coord_data = pd.DataFrame(hdf.SD(self.geo_file_paths[0], hdf.SDC.READ).select(coord_type).get()).head(0)

        for path in self.geo_file_paths:
            coord_data = pd.concat([coord_data, pd.DataFrame(hdf.SD(path, hdf.SDC.READ).select(self.datatype).get())])

        return coord_data

