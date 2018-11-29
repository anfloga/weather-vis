import interface
import os
import pandas as pd
import numpy as np
from shapely.geometry import mapping
from shapely import geometry
from matplotlib.tri.triangulation import Triangulation
from .topography_service import TopographyService
from ..models.swath_tile import SwathTile


class SatelliteService(interface.implements(TopographyService)):

    def __init__(self, datatype, path_string, geo_directory = None, data_directory = None):
        self.swath_tiles = []
        self.x_scale = 100
        self.y_scale = 100
        self.datatype = datatype
        self.path_string = path_string

        if geo_directory is not None and data_directory is not None:
            self.__add_directory__(geo_directory, data_directory)

    def __get_variable_dataframe__(self, tile):
        raise NotImplementedError()

    def __get_geo_dataframe__(self, tile, coord_type):
        raise NotImplementedError()

    def __add_directory__(self, geo_directory, data_directory):
        data_list = sorted(os.listdir(data_directory))
        geo_list = sorted(os.listdir(geo_directory))

        dir_length = len(geo_list)

        for i in range(dir_length):
            geo_filename = os.fsdecode(geo_directory) + "/" + os.fsdecode(geo_list[i])
            data_filename = os.fsdecode(data_directory) + "/" + os.fsdecode(data_list[i])
            tile = SwathTile(geo_filename, data_filename)
            self.add(tile)

    def add(self, swath_tile):
        print('tile added')

        self.swath_tiles.append(swath_tile)

    def query(self, query):
        for tile in self.swath_tiles:
            x, y = tile.bounds.exterior.coords.xy

            if tile.bounds.contains(query):
                return self.__get_frame__(tile, query)

    def __get_frame__(self, tile, query_bounds):
        df = self.__to_grid__(tile, query_bounds)
        df = self.__to_local__(df, query_bounds, 100)
        return self.__get_json__(df)

    def __to_grid__(self, tile, query):
        variable_dataframe = self.__get_variable_dataframe__(tile)
        lat_dataframe = self.__get_geo_dataframe__(tile, "Latitude")
        long_dataframe = self.__get_geo_dataframe__(tile, "Longitude")

        lat_stack = pd.DataFrame()
        long_stack = pd.DataFrame()
        type_stack = pd.DataFrame()

        #stack the columns
        for column in lat_dataframe:
            lat_stack = pd.concat([lat_stack, lat_dataframe[column]])
        for column in long_dataframe:
            long_stack = pd.concat([long_stack, long_dataframe[column]])
        for column in variable_dataframe:
            type_stack = pd.concat([type_stack, variable_dataframe[column]])

        df = pd.concat([lat_stack[lat_stack.columns[0]], long_stack[long_stack.columns[0]], type_stack[type_stack.columns[0]]], axis=1, keys=["lat", "long", self.datatype])

        bounds = query.bounds
        #lat is LT upper lat and GT lower lat; long is GT west long and LT east long
        df = df.loc[(df["lat"] < bounds[3]) & (df["lat"] > bounds[1]) & (df["long"] > bounds[0]) & (df["long"] < bounds[2])]
        return df


    def __to_local__(self, df, query, scale):
        df[self.datatype][df[self.datatype] < 0] = 0

        query_bounds = query.bounds

        lat_span = int(round(((query_bounds[3] + 180) - (query_bounds[1] + 180)) * 50))
        long_span = int(round(((query_bounds[2] + 180) - (query_bounds[0] + 180)) * 50))

        lat_quotient = 100 / lat_span
        long_quotient = 100 / long_span
        df["x"] = df["long"].apply(lambda x: x * long_quotient * scale)
        df["y"] = df["lat"].apply(lambda y: y * lat_quotient * scale)

        return df

    def __get_json__(self, df):
        layer_frame = pd.DataFrame(columns=["x", "y", "z"])

        for col in layer_frame:
            layer_frame[col] = pd.to_numeric(layer_frame[col], errors='coerce')

        x = df["x"]
        y = df["y"]
        z = np.asarray(df[self.datatype])

        tri, args, kwargs = Triangulation.get_from_args_and_kwargs(x, y, z)
        triangles = tri.get_masked_triangles()

        xt = tri.x[triangles]
        yt = tri.y[triangles]
        zt = z[triangles]
        verts = np.stack((xt, yt, zt), axis=-1)

        columns= ["a", "b", "c"]

        arrays = [["a", "b", "c"],["x", "y", "z"]]
        tuples = list(zip(*arrays))
        index = pd.MultiIndex.from_tuples(tuples, names=['vector', 'vertex'])

        vertdf = pd.DataFrame.from_records(verts, columns=columns)

        adf = pd.DataFrame()
        bdf = pd.DataFrame()
        cdf = pd.DataFrame()

        adf[['ax','ay','az']] = pd.DataFrame(vertdf.a.values.tolist())
        bdf[['bx','by','bz']] = pd.DataFrame(vertdf.b.values.tolist())
        cdf[['cx','cy','cz']] = pd.DataFrame(vertdf.c.values.tolist())

        result = pd.concat([adf, bdf, cdf], axis=1)

        result = result.drop(result[((result.az == 65535) | (result.bz == 65535) | (result.cz == 65535))].index)

        return result.to_json(orient="records")


