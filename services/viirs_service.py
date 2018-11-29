import pandas as pd
import h5py as hdf
from .satellite_service import SatelliteService

class ViirsService(SatelliteService):

    def __get_variable_dataframe__(self, tile):
        variable_data = pd.DataFrame(hdf.File(tile.data_file_path)['All_Data'][self.path_string][self.datatype][:])
        return variable_data

    def __get_geo_dataframe__(self, tile, coord_type):
        coord_data = pd.DataFrame(hdf.File(tile.geo_file_path)['All_Data']['VIIRS-CLD-AGG-GEO_All'][coord_type][:])
        return coord_data

    def __init__(self, datatype, path_string, geo_directory = None, data_directory = None):
        super().__init__(datatype, path_string, geo_directory, data_directory)


