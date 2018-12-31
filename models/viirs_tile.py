import pandas as pd
import h5py as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from .swath_tile import SwathTile
from ..geoutils import geoutils as gu


class ViirsTile(SwathTile):

    def __init__(self, datatype, path_string, geo_file_paths, data_file_paths):
        super().__init__(datatype, geo_file_paths, data_file_paths)

        self.path_string = path_string
        self.geo_path_string = 'VIIRS-CLD-AGG-GEO_All'

        long_data = pd.DataFrame(hdf.File(geo_file_paths[0])['All_Data'][self.geo_path_string]['Longitude'][:]).head(0)
        lat_data = pd.DataFrame(hdf.File(geo_file_paths[0])['All_Data'][self.geo_path_string]['Latitude'][:]).head(0)

        for path in geo_file_paths:
            geo_data_file = hdf.File(path)
            long_data = pd.concat([long_data, pd.DataFrame(geo_data_file['All_Data'][self.geo_path_string]['Longitude'][:])])
            lat_data = pd.concat([lat_data, pd.DataFrame(geo_data_file['All_Data'][self.geo_path_string]['Latitude'][:])])

        self.bounds = self.__calculate_bounds__(lat_data, long_data)

    def __get_variable_dataframe__(self):
        variable_data = pd.DataFrame(hdf.File(self.data_file_paths[0])['All_Data'][self.path_string][self.datatype][:]).head(0)

        for path in self.data_file_paths:
            variable_data = pd.concat([variable_data, pd.DataFrame(hdf.File(path)['All_Data'][self.path_string][self.datatype][:])])

        return variable_data

    def __get_geo_dataframe__(self, coord_type):
        coord_data = pd.DataFrame(hdf.File(self.geo_file_paths[0])['All_Data'][self.geo_path_string][coord_type][:]).head(0)

        for path in self.geo_file_paths:
            coord_data = pd.concat([coord_data, pd.DataFrame(hdf.File(path)['All_Data'][self.geo_path_string][coord_type][:])])

        return coord_data

