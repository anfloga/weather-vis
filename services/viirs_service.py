import pandas as pd
import h5py as hdf
from .satellite_service import SatelliteService
from ..models.viirs_tile import ViirsTile

class ViirsService(SatelliteService):

    def __get_tile__(self, geo_filename, data_filename):
        return ViirsTile(self.datatype, self.path_string, geo_filename, data_filename)

    def __init__(self, datatype, path_string, x_scale = 100, y_scale = 100, z_scale = 100, geo_directory = None, data_directory = None):
        super().__init__(datatype, path_string, x_scale, y_scale, z_scale, geo_directory, data_directory)


