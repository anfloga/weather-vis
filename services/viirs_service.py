import pandas as pd
import h5py as hdf
from .satellite_service import SatelliteService
from ..models.viirs_tile import ViirsTile

class ViirsService(SatelliteService):

    def __get_variable_dataframe__(self, tile):
        variable_data = pd.DataFrame(hdf.File(tile.data_file_path)['All_Data'][self.path_string][self.datatype][:])
        return variable_data

    def __get_geo_dataframe__(self, tile, coord_type):
        coord_data = pd.DataFrame(hdf.File(tile.geo_file_path)['All_Data']['VIIRS-CLD-AGG-GEO_All'][coord_type][:])
        return coord_data

    def __get_tile__(self, geo_filename, data_filename):
        return ViirsTile(geo_filename, data_filename)

    def __init__(self, datatype, path_string, x_scale = 100, y_scale = 100, z_scale = 100, geo_directory = None, data_directory = None):
        super().__init__(datatype, path_string, x_scale, y_scale, z_scale, geo_directory, data_directory)


