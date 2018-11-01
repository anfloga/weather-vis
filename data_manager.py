import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate
from matplotlib.tri.triangulation import Triangulation

import datetime as dt
#import pyhdf.SD as hdf
import h5py as hdf
import os
import geoutils as gu



class SwathTileManager:

    def __init__(self, data_directory, geo_directory):
        self.data_directory = data_directory
        self.geo_directory = geo_directory
        self.swath_tile_list = []

    def set_current_geometry(self, geometry):
        self.geometry = geometry

    def query_tiles(self, path, datatype, bounding_box):
        #data_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/cbh")
        #geo_directory = os.fsencode("/media/joe/DATA/weather_data/viirs/20180916/geo")

        geo_directory = self.geo_directory
        data_directory = self.data_directory

        data_list = sorted(os.listdir(data_directory))
        geo_list = sorted(os.listdir(geo_directory))

        dir_length = len(geo_list)

        for i in range(dir_length):
            geo_filename = os.fsdecode(geo_directory) + "/" + os.fsdecode(geo_list[i])
            data_filename = os.fsdecode(data_directory) + "/" + os.fsdecode(data_list[i])
            tile = SwathTile(geo_filename, data_filename)
            if self.bound_in_tile(tile, bounding_box):
                self.add_tile_to_list(tile)

        return self.get_merged_swath_dataframe(path, datatype, bounding_box)

    def bound_in_tile(self, swath_tile, bounding_box):
        #swath_tile.bounding_box.print_geometries()
        #bounding_box.print_geometries()
        if gu.polygon_contain(swath_tile.bounding_box, bounding_box):
            return True
        return False

    def add_tile_to_list(self, swath_tile):
        self.swath_tile_list.append(swath_tile)
        self.update_merged_swath_bounds()
        print("tile added: " + swath_tile.geo_file_path)
        if len(self.swath_tile_list) > 3:
            swath_tile_list.pop(0)

    def update_merged_swath_bounds(self):
        direction = self.direction_of_travel(self.swath_tile_list)

        if direction == 'N':
            north_tile_index = len(self.swath_tile_list) - 1
            south_tile_index = 0
        if direction == 'S':
            north_tile_index = 0
            south_tile_index = len(self.swath_tile_list) - 1

        corner_1 = {'lat': self.swath_tile_list[north_tile_index].bounding_box.corners[0]['lat'], 'long': self.swath_tile_list[north_tile_index].bounding_box.corners[0]['long']}
        corner_2 = {'lat': self.swath_tile_list[north_tile_index].bounding_box.corners[1]['lat'], 'long': self.swath_tile_list[north_tile_index].bounding_box.corners[1]['long']}
        corner_3 = {'lat': self.swath_tile_list[south_tile_index].bounding_box.corners[2]['lat'], 'long': self.swath_tile_list[south_tile_index].bounding_box.corners[2]['long']}
        corner_4 = {'lat': self.swath_tile_list[south_tile_index].bounding_box.corners[3]['lat'], 'long': self.swath_tile_list[south_tile_index].bounding_box.corners[3]['long']}

        self.merged_swath_bounds = BoundingBox(corner_1, corner_2, corner_3, corner_4)

    def direction_of_travel(self, swath_tile_list):
        oldest_lat = swath_tile_list[0].bounding_box.corners[0]['lat']
        youngest_lat = swath_tile_list[len(swath_tile_list) - 1].bounding_box.corners[0]['lat']

        if gu.point_south_of_bound(oldest_lat, youngest_lat):
            return 'S'
        else:
            return 'N'

    def get_merged_swath_dataframe(self, path, data_type, bounding_box):

        bounding_box.print_geometries()

        if gu.point_north_of_bound(bounding_box.corners[0]["lat"], bounding_box.corners[1]["lat"]):
            upper_lat = bounding_box.corners[1]["lat"]
            lower_lat = bounding_box.corners[3]["lat"]
        else:
            upper_lat = bounding_box.corners[0]["lat"]
            lower_lat = bounding_box.corners[2]["lat"]

        if gu.point_west_of_bound(bounding_box.corners[0]["long"],bounding_box.corners[2]["long"]):
            west_long = bounding_box.corners[2]["long"]
            east_long = bounding_box.corners[1]["long"]
        else:
            west_long = bounding_box.corners[0]["long"]
            east_long = bounding_box.corners[3]["long"]

        merged_dataframe = pd.DataFrame()
        lat_dataframe = pd.DataFrame()
        long_dataframe = pd.DataFrame()

        #print(len(self.swath_tile_list))

        for tile in self.swath_tile_list:
            merged_dataframe = pd.concat([merged_dataframe, tile.get_variable_dataframe(path, data_type)])
            lat_dataframe = pd.concat([lat_dataframe, tile.get_geo_dataframe("Latitude")])
            long_dataframe = pd.concat([long_dataframe, tile.get_geo_dataframe("Longitude")])

        lat_stack = pd.DataFrame()
        long_stack = pd.DataFrame()
        type_stack = pd.DataFrame()

        #stack the columns
        for column in lat_dataframe:
            lat_stack = pd.concat([lat_stack, lat_dataframe[column]])
        for column in long_dataframe:
            long_stack = pd.concat([long_stack, long_dataframe[column]])
        for column in merged_dataframe:
            type_stack = pd.concat([type_stack, merged_dataframe[column]])

        merged_stack = pd.concat([lat_stack[lat_stack.columns[0]], long_stack[long_stack.columns[0]], type_stack[type_stack.columns[0]]], axis=1, keys=["lat", "long", data_type])

        #lat is LT upper lat and GT lower lat and long is GT west long and LT east long
        #merged_stack = merged_stack.loc[(merged_stack["lat"] < upper_lat) & (merged_stack["lat"] > lower_lat) & (merged_stack["long"] > west_long) & (merged_stack["long"] < east_long)]
        merged_stack = merged_stack.loc[(merged_stack["lat"] < bounding_box.max_lat) & (merged_stack["lat"] > bounding_box.min_lat) & (merged_stack["long"] > bounding_box.min_long) & (merged_stack["long"] < bounding_box.max_long)]

        #convert to local
        merged_stack["x"] = merged_stack["lat"].apply(lambda x: (x - bounding_box.min_lat) * 1200)
        merged_stack["y"] = merged_stack["long"].apply(lambda x: (x - bounding_box.min_long) * 500)
        merged_stack[data_type][merged_stack[data_type] < 0] = 0

        return merged_stack

    def get_local_point(self, minimum, point):
        #1 deg = 100 px
        #if minimum < 0 && point < 0:
        #    return (point - minimum)

        #if minimum < 0 && point > 0:
        #    return (point - minimum)
        return (point - minimum) * 400


    def build_layer_map(self, data_type, bounding_box):
        lat_span = int(round(((bounding_box.max_lat + 180) - (bounding_box.min_lat + 180)) * 50))
        long_span = int(round(((bounding_box.max_long + 180) - (bounding_box.min_long + 180)) * 50))

        lat_quotient = 100 / lat_span
        long_quotient = 100 / long_span

        self.geometry["x"] = self.geometry["x"].apply(lambda x: x * long_quotient)
        self.geometry["y"] = self.geometry["y"].apply(lambda y: y * lat_quotient)

        layer_frame = pd.DataFrame(columns=["x", "y", "z"])

        for col in layer_frame:
            layer_frame[col] = pd.to_numeric(layer_frame[col], errors='coerce')


       # layer_frame["x"] = self.geometry["x"]
       # layer_frame["y"] = self.geometry["y"]
       # layer_frame["z"] = self.geometry["Cloud_Top_Height"]

        x = self.geometry["x"]
        y = self.geometry["y"]
        z = np.asarray(self.geometry[data_type])


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

        #self.layer = result.head(10000).to_json(orient="records")
        result = self.filter_dataframe(result)
        self.layer = result.to_json(orient="records")


    def get_vertex(self, xt, yt, zt):
        #arrays = [["a", "b", "c"],["x", "y", "z"]]
        vert = np.array([xt[0], yt[0], zt[0], xt[1], yt[1], zt[1], xt[2], yt[2], zt[2]])
        #tuples = list(zip(*arrays))
        #index = pd.MultiIndex.from_tuples(tuples, names=['vector', 'vertex'])
        columns = ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2"]
        df = pd.DataFrame(vert)
        return df

    def filter_dataframe(self, df):
        """docstring for filter_dataframe"""
        #dataframe = dataframe.drop(dataframe[((dataframe[['az','bz','cz']].max(axis=1) - dataframe[['az','bz','cz']].min(axis=1)) > 10000)].index)

        #df = df.drop(df[(df.score < 50) & (df.score > 20)].index)

        #dataframe = dataframe.drop(dataframe[((dataframe[['az','bz','cz']].max(axis=1) - dataframe[['az','bz','cz']].min(axis=1)) > 65000)].index)
        df = df.drop(df[((df.az == 65535) | (df.bz == 65535) | (df.cz == 65535))].index)

        #df = df.drop(df[(df.az < 50) & (df.score > 20)].index)

        return df


    def plot_plane(self, layer_frame):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(layer_frame["x"], layer_frame["y"], layer_frame["z"], cmap=plt.cm.viridis, linewidth=0.2)
        plt.show()

    def interpolate_plane(self, layer_frame):
        layer_frame["z"].replace(0, np.nan, inplace=True)

        known = layer_frame.loc[layer_frame["z"].notnull()]
        extremeknown = pd.DataFrame([[0,0,0], [100,100,0], [0,100,0], [100,0,0]], columns=list('xyz'))
        known.dropna(inplace=True)

        knownpoints = known[["x","y"]]
        points = knownpoints.as_matrix()

        x = np.linspace(0, 100, 101)
        y = np.linspace(0, 100, 101)
        X, Y = np.meshgrid(x,y)

        zi = interpolate.griddata(points, known["z"], (X, Y), method='cubic', fill_value=0)
        layer_frame = pd.DataFrame()

        for xi in x:
            for yi in y:
                data = {"x": xi, "y": yi, "z": zi[int(xi)][int(yi)]}
                layer_frame = pd.concat([layer_frame, pd.DataFrame(data, index=[0])])

        return layer_frame
