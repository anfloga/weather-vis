import pandas as pd
import h5py as hdf
import datetime as dt
import numpy as np
from shapely import geometry
from .swath_tile import SwathTile
from ..geoutils import geoutils as gu


class ViirsTile(SwathTile):

    def __init__(self, geo_file_path, data_file_path):
        self.geo_file_path = geo_file_path
        self.data_file_path = data_file_path

        geo_data_file = hdf.File(geo_file_path)
        long_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Longitude'][:])
        lat_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Latitude'][:])

        self.bounds = self.__calculate_bounds__(lat_data, long_data)
        self.timestamp = dt.datetime.now()

