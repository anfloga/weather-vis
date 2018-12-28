import pandas as pd
import pyhdf.SD as hdf
from .satellite_service import SatelliteService
from ..models.modis_tile import ModisTile

class ModisService(SatelliteService):

    def __get_variable_dataframe__(self, tile):
        variable_data = pd.DataFrame(hdf.SD(tile.data_file_path, hdf.SDC.READ).select(self.datatype).get())
        return variable_data

    def __get_geo_dataframe__(self, tile, coord_type):
        coord_data = pd.DataFrame(hdf.SD(tile.geo_file_path, hdf.SDC.READ).select(coord_type).get())
        return coord_data

    def __get_tile__(self, geo_filename, data_filename):
        return ModisTile(geo_filename, data_filename)

    def __init__(self, datatype, path_string, x_scale = 100, y_scale = 100, z_scale = 100, geo_directory = None, data_directory = None):
        super().__init__(datatype, path_string, x_scale, y_scale, z_scale, geo_directory, data_directory)


