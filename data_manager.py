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

class SwathTile:

    def get_variable_dataframe(self, path, data_type):
        #lat_data = pd.DataFrame(data_file.select('Latitude').get())
        #long_data = pd.DataFrame(data_file.select('Longitude').get())
        #variable_data = pd.DataFrame(pd.HDFStore(self.data_file_path)['All_Data']['VIIRS-CBH-EDR_All'][data_type])

        #variable_data = pd.read_hdf(self.data_file_path, 'All_Data/VIIRS-CBH-EDR_All')[data_type]

        print("DATA FILE PATH:")
        print(self.data_file_path)
        variable_data = pd.DataFrame(hdf.File(self.data_file_path)['All_Data'][path][data_type][:])

        #variable_data = pd.read_hdf(data_file['All_Data']['VIIRS-CBH-EDR_All'][data_type])
        return variable_data

    def get_geo_dataframe(self, coord_type):
        coord_data = pd.DataFrame(hdf.File(self.geo_file_path)['All_Data']['VIIRS-CLD-AGG-GEO_All'][coord_type][:])
        return coord_data

    def __init__(self, geo_file_path, data_file_path):

        print(geo_file_path)
        print(data_file_path)
        self.geo_file_path = geo_file_path
        self.data_file_path = data_file_path
        #geo_data_file = hdf.File(geo_file_path, 'r')

        print(geo_file_path)
        #geo_data_file = pd.read_hdf(geo_file_path, 'All_Data')

        geo_data_file = hdf.File(geo_file_path)
        long_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Longitude'][:])
        lat_data = pd.DataFrame(geo_data_file['All_Data']['VIIRS-CLD-AGG-GEO_All']['Latitude'][:])

        self.bounding_box = self.__calculate_bounds__(lat_data, long_data)
        self.bounding_box = self.__calculate_bounds__(lat_data, long_data)
        self.timestamp = dt.datetime.now()

    def __calculate_bounds__(self, latitude_dataframe, longitude_dataframe):
        corner_1 = {'lat': latitude_dataframe.iloc[0,0], 'long': longitude_dataframe.iloc[0,0]}
        corner_2 = {'lat': latitude_dataframe.iloc[0,-1], 'long': longitude_dataframe.iloc[0,-1]}
        corner_3 = {'lat': latitude_dataframe.iloc[-1,0], 'long': longitude_dataframe.iloc[-1,0]}
        corner_4 = {'lat': latitude_dataframe.iloc[-1,-1], 'long': longitude_dataframe.iloc[-1,-1]}

        corner_list = [corner_1, corner_2, corner_3, corner_4]

        corner_list = gu.sort_coordinates(corner_list)

        bounding_box = BoundingBox(corner_list[0], corner_list[1], corner_list[2], corner_list[3])
        return bounding_box


class BoundingBox:

    def __init__(self, corner_1, corner_2, corner_3, corner_4, debug=False):
        self.corners = []
        self.corners.append(corner_1)
        self.corners.append(corner_2)
        self.corners.append(corner_3)
        self.corners.append(corner_4)
        self.get_extremes()
        self.debug = debug

    def print_geometries(self):
        for corner in self.corners:
            print(*list(corner.values()))

    def get_extremes(self):
        self.min_long = self.corners[0]['long']
        self.min_long_corner = 0

        self.max_long = self.corners[0]['long']
        self.max_long_corner = 0

        self.min_lat = self.corners[0]['lat']
        self.min_lat_corner = 0

        self.max_lat = self.corners[0]['lat']
        self.max_lat_corner = 0

        i = 0

        for corner in self.corners:

            #print(corner['long'])
            if corner['long'] < self.min_long:
                self.min_long = corner['long']
                self.min_long_corner = i

            if corner['long'] > self.max_long:
                self.max_long = corner['long']
                self.max_long_corner = i

            if corner['lat'] < self.min_lat:
                self.min_lat = corner['lat']
                self.min_lat_corner = i

            if corner['lat'] > self.max_lat:
                self.max_lat = corner['lat']
                self.max_lat_corner = i

            i = i + 1


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

        print("in query_tiles, data directory is " + os.fsdecode(self.data_directory))
        geo_directory = self.geo_directory
        data_directory = self.data_directory

        data_list = os.listdir(data_directory)
        geo_list = os.listdir(geo_directory)

        dir_length = len(geo_list)

        for i in range(dir_length):
            geo_filename = os.fsdecode(geo_directory) + "/" + os.fsdecode(geo_list[i])
            data_filename = os.fsdecode(data_directory) + "/" + os.fsdecode(data_list[i])
            tile = SwathTile(geo_filename, data_filename)
            if self.bound_in_tile(tile, bounding_box):
                self.add_tile_to_list(tile)

        return self.get_merged_swath_dataframe(path, datatype, bounding_box)

    def bound_in_tile(self, swath_tile, bounding_box):
        swath_tile.bounding_box.print_geometries()
        bounding_box.print_geometries()
        if gu.bounding_box_within_swath(swath_tile.bounding_box, bounding_box):
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

        print(len(self.swath_tile_list))

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

        print(merged_stack.shape)
        print(upper_lat)
        print(lower_lat)
        print(west_long)
        print(east_long)

        #lat is LT upper lat and GT lower lat and long is GT west long and LT east long
        #merged_stack = merged_stack.loc[(merged_stack["lat"] < upper_lat) & (merged_stack["lat"] > lower_lat) & (merged_stack["long"] > west_long) & (merged_stack["long"] < east_long)]
        merged_stack = merged_stack.loc[(merged_stack["lat"] < bounding_box.max_lat) & (merged_stack["lat"] > bounding_box.min_lat) & (merged_stack["long"] > bounding_box.min_long) & (merged_stack["long"] < bounding_box.max_long)]

        #convert to local
        merged_stack["x"] = merged_stack["lat"].apply(lambda x: (x - bounding_box.min_lat) * 800)
        merged_stack["y"] = merged_stack["long"].apply(lambda x: (x - bounding_box.min_long) * 50)
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

        print(lat_span)
        print(long_span)

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

        #print(verts)

        print(xt)
        print(yt)
        print(zt)

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

        print(result.head().to_json(orient="records"))

        #self.layer = result.head(10000).to_json(orient="records")
        #result = self.filter_dataframe(result)
        self.layer = result.to_json(orient="records")


    def get_vertex(self, xt, yt, zt):
        #arrays = [["a", "b", "c"],["x", "y", "z"]]
        vert = np.array([xt[0], yt[0], zt[0], xt[1], yt[1], zt[1], xt[2], yt[2], zt[2]])
        #tuples = list(zip(*arrays))
        #index = pd.MultiIndex.from_tuples(tuples, names=['vector', 'vertex'])
        columns = ["x0", "y0", "z0", "x1", "y1", "z1", "x2", "y2", "z2"]
        df = pd.DataFrame(vert)
        return df

    def filter_dataframe(self, dataframe):
        """docstring for filter_dataframe"""
        print(dataframe.shape)
        dataframe = dataframe.drop(dataframe[((dataframe[['az','bz','cz']].max(axis=1) - dataframe[['az','bz','cz']].min(axis=1)) > 10000)].index)
        print(dataframe.shape)
        return dataframe


    def plot_plane(self, layer_frame):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_trisurf(layer_frame["x"], layer_frame["y"], layer_frame["z"], cmap=plt.cm.viridis, linewidth=0.2)
        plt.show()

    def interpolate_plane(self, layer_frame):
        print(layer_frame.head())
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
                print(layer_frame.shape)

        print(layer_frame.head(100))
        print("finished")
        return layer_frame
