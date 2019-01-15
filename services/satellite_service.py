import interface
import os
import math
import pandas as pd
import numpy as np
import pyproj as proj
from shapely.geometry import mapping
from shapely import geometry
import matplotlib.pyplot as plt
from matplotlib.tri.triangulation import Triangulation
from .topography_service import TopographyService
from ..models.swath_tile import SwathTile


class SatelliteService(interface.implements(TopographyService)):

    def __init__(self, datatype, path_string, x_scale = 100, y_scale = 100, z_scale = 100, geo_directory = None, data_directory = None):
        self.swath_tiles = []
        self.x_scale = x_scale
        self.y_scale = y_scale
        self.z_scale = z_scale
        self.datatype = datatype
        self.path_string = path_string
        self.in_projection = proj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
        self.out_projection = proj.Proj(init='epsg:3857')

        if geo_directory is not None and data_directory is not None:
            self.__add_directory__(geo_directory, data_directory)

    def __get_tile__(self, geo_filename, data_filename):
        raise NotImplementedError()

    def __add_directory__(self, geo_directory, data_directory):
        data_list = sorted(os.listdir(data_directory))
        geo_list = sorted(os.listdir(geo_directory))

        dir_length = len(geo_list)

        for i in range(dir_length):
            geo_filename = os.fsdecode(geo_directory) + "/" + os.fsdecode(geo_list[i])
            data_filename = os.fsdecode(data_directory) + "/" + os.fsdecode(data_list[i])
            tile = self.__get_tile__([geo_filename], [data_filename])
            self.add(tile)

    def add(self, swath_tile):
        print('tile added')

        self.swath_tiles.append(swath_tile)

    def query(self, query):
        track = self.swath_tiles[0]

        if len(self.swath_tiles) > 1:
            for i in range(1, len(self.swath_tiles)):
                track = track.merge(self.swath_tiles[i])

        print(track.bounds.contains(query.projected_shape))

        if track.bounds.contains(query.projected_shape):
            return self.__get_frame__(track, query.query_shape)

    def __get_frame__(self, tile, query_bounds):
        df = self.__to_grid__(tile, query_bounds)
        df = self.__to_local__(df, query_bounds, self.z_scale)
        return self.__get_json__(df)

    def __to_grid__(self, tile, query):
        variable_dataframe = tile.__get_variable_dataframe__()
        lat_dataframe = tile.__get_geo_dataframe__("Latitude")
        long_dataframe = tile.__get_geo_dataframe__("Longitude")

        df = pd.concat([lat_dataframe, long_dataframe, variable_dataframe], axis=1, keys=['lat', 'long', self.datatype, 'timestamp'], ignore_index=True)
        df.columns = ['lat', 'long', self.datatype, 'timestamp']

        bounds = query.bounds

        df = df.loc[(df["lat"] < bounds[3]) & (df["lat"] > bounds[1]) & (df["long"] > bounds[0]) & (df["long"] < bounds[2])]
        return df

    def __scale_z__(self, df, scale):
        max_z = df[self.datatype].max()
        min_z = df[self.datatype].min()

        df[self.datatype] = df[self.datatype].apply(lambda z: (scale * ((z - min_z) / (max_z - min_z))))
        return df

    def __project__(self, row):
        x2,y2 = proj.transform(self.in_projection, self.out_projection, row['long'], row['lat'])

        return pd.Series([x2, y2])

    def __to_local__(self, df, query, scale):
        df[self.datatype][df[self.datatype] < 0] = 0
        df[self.datatype][df[self.datatype] == 65535] = 0
        df = df.reset_index(drop=True)

        df = self.__scale_z__(df, scale)

        x_origin,y_origin = proj.transform(self.in_projection, self.out_projection, query.centroid.coords[0][0], query.centroid.coords[0][1])

        df[["x","y"]] = df.apply(self.__project__, axis=1)

        df["x"] = df["x"].apply(lambda x: (x_origin - x) * 0.001)
        df["y"] = df["y"].apply(lambda y: (y_origin - y) * 0.001)
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
        #result = result.drop(result[((result.az == 65535) | (result.bz == 65535) | (result.cz == 65535))].index)
        #result = result.drop(result[((result.az == 0) | (result.bz == 0) | (result.cz == 0))].index)

        return result.to_json(orient="records")


