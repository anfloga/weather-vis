import pandas as pd
import pyhdf.SD as hdf
from .satellite_service import SatelliteService
from ..models.modis_tile import ModisTile

class ModisService(SatelliteService):

    def __get_tile__(self, geo_filename, data_filename):
        return ModisTile(self.datatype, geo_filename, data_filename)

    def __init__(self, datatype, path_string, x_scale = 100, y_scale = 100, z_scale = 100, geo_directory = None, data_directory = None):
        super().__init__(datatype, path_string, x_scale, y_scale, z_scale, geo_directory, data_directory)


