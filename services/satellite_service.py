import interface
import os
import math
import pandas as pd
import numpy as np
import pyproj as proj
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
        self.in_projection = proj.Proj(init='epsg:4326') # assuming you're using WGS84 geographic
        #self.out_projection = proj.Proj(init='epsg:27700') # use a locally appropriate projected CRS
        self.out_projection = proj.Proj(init='epsg:3857')

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

    def __get_x__(self, lon, width):
        return int(round(math.fmod((width * (180.0 + lon) / 360.0), (1.5 * width))))

    def __get_y__(self, lat, width, height):
        lat_rad = lat * math.pi / 180.0
        merc = 0.5 * math.log( (1 + math.sin(lat_rad)) / (1 - math.sin(lat_rad)) )
        return int(round((height / 2) - (width * merc / (2 * math.pi))))

    def __project__(self, row):
        #print(row['long'])
        #print(row['lat'])

        x2,y2 = proj.transform(self.in_projection, self.out_projection, row['long'], row['lat'])
        #x2,y2 = self.in_projection(row['long'], row['lat'])

        return pd.Series([x2, y2])

    def __to_local__(self, df, query, scale):
        df[self.datatype][df[self.datatype] < 0] = 0

        query_bounds = query.bounds

        #x_origin = self.__get_x__(query.centroid.coords[0][1], 10000)
        #y_origin = self.__get_y__(query.centroid.coords[0][0], 10000, 10000)
        print((query.centroid.coords[0][1],query.centroid.coords[0][0]))
        #x_origin,y_origin = self.in_projection(query.centroid.coords[0][0],query.centroid.coords[0][1])
        x_origin,y_origin = proj.transform(self.in_projection, self.out_projection, query.centroid.coords[0][0], query.centroid.coords[0][1])

        #df["x"] = df["lat"].apply(self.__get_x__, args=(10000,))
        #df["y"] = df["long"].apply(self.__get_y__, args=(10000,10000))

        #df["x"] = df["x"].apply(lambda x: x - x_origin)
        #df["y"] = df["y"].apply(lambda y: y - y_origin)

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
        result = result.drop(result[((result.az == 65535) | (result.bz == 65535) | (result.cz == 65535))].index)
        print(result.head(100))
        return result.to_json(orient="records")


