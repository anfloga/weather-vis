import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy import interpolate

import datetime as dt
import pyhdf.SD as hdf
import os
import geoutils as gu

class SwathTile:

    def get_dataframe(self, data_type):
        data_file = hdf.SD(self.file_path, hdf.SDC.READ)
        #lat_data = pd.DataFrame(data_file.select('Latitude').get())
        #long_data = pd.DataFrame(data_file.select('Longitude').get())
        variable_data = pd.DataFrame(data_file.select(data_type).get())
        return variable_data

    def __init__(self, file_path):
        self.file_path = file_path
        data_file = hdf.SD(file_path, hdf.SDC.READ)
        lat_data = pd.DataFrame(data_file.select('Latitude').get())
        long_data = pd.DataFrame(data_file.select('Longitude').get())
        self.bounding_box = self.__calculate_bounds__(lat_data, long_data)
        self.timestamp = dt.datetime.now()

    def __calculate_bounds__(self, latitude_dataframe, longitude_dataframe):
        corner_1 = {'lat': latitude_dataframe.iloc[0,0], 'long': longitude_dataframe.iloc[0,0]}
        corner_2 = {'lat': latitude_dataframe.iloc[0,-1], 'long': longitude_dataframe.iloc[0,-1]}
        corner_3 = {'lat': latitude_dataframe.iloc[-1,0], 'long': longitude_dataframe.iloc[-1,0]}
        corner_4 = {'lat': latitude_dataframe.iloc[-1,-1], 'long': longitude_dataframe.iloc[-1,-1]}
        bounding_box = BoundingBox(corner_1, corner_2, corner_3, corner_4)
        return bounding_box


class BoundingBox:

    def __init__(self, corner_1, corner_2, corner_3, corner_4):
        self.corners = []
        self.corners.append(corner_1)
        self.corners.append(corner_2)
        self.corners.append(corner_3)
        self.corners.append(corner_4)
        self.get_extremes()

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

    swath_tile_list = []

    def set_current_geometry(self, geometry):
        self.geometry = geometry

    def query_tiles(self, datatype, bounding_box):
        directory = os.fsencode("/media/joe/DATA/weather_data/raw/201811322")
        for file in os.listdir(directory):
            filename = os.fsdecode(directory) + "/" + os.fsdecode(file)
            print(filename)
            tile = SwathTile(filename)
            if self.bound_in_tile(tile, bounding_box):
                self.add_tile_to_list(tile)
        return self.get_merged_swath_dataframe(datatype, bounding_box)

    def bound_in_tile(self, swath_tile, bounding_box):
        if gu.bounding_box_within_swath(bounding_box, swath_tile.bounding_box):
            return True
        return False

    def add_tile_to_list(self, swath_tile):
        self.swath_tile_list.append(swath_tile)
        self.update_merged_swath_bounds()
        print("tile added: " + swath_tile.file_path)
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

    def get_merged_swath_dataframe(self, data_type, bounding_box):

        if gu.point_north_of_bound(bounding_box.corners[0]["lat"], bounding_box.corners[1]["lat"]):
            upper_lat = bounding_box.corners[1]["lat"]
            lower_lat = bounding_box.corners[3]
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

        for tile in self.swath_tile_list:
            merged_dataframe = pd.concat([merged_dataframe, tile.get_dataframe(data_type)])
            lat_dataframe = pd.concat([lat_dataframe, tile.get_dataframe("Latitude")])
            long_dataframe = pd.concat([long_dataframe, tile.get_dataframe("Longitude")])

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
        merged_stack = merged_stack.loc[(merged_stack["lat"] < upper_lat) & (merged_stack["lat"] > lower_lat) & (merged_stack["long"] > west_long) & (merged_stack["long"] < east_long)]
        #merged_stack = merged_stack.loc[(merged_stack["lat"] > lower_lat)]

        #convert to local
        merged_stack["x"] = merged_stack["lat"].apply(lambda x: (x - bounding_box.min_lat) * 50)
        merged_stack["y"] = merged_stack["long"].apply(lambda x: (x - bounding_box.min_long) * 50)

        merged_stack = merged_stack.drop(merged_stack[merged_stack.Cloud_Top_Height < 0].index)
        merged_stack["Cloud_Top_Height"] = merged_stack["Cloud_Top_Height"].apply(lambda x: x / 20)

        #merged_stack.to_csv("out.csv")
        return merged_stack

    def get_local_point(self, minimum, point):
        #1 deg = 100 px
        #if minimum < 0 && point < 0:
        #    return (point - minimum)

        #if minimum < 0 && point > 0:
        #    return (point - minimum)
        return (point - minimum) * 100


    def build_layer_map(self, bounding_box):
        lat_span = int(round(((bounding_box.max_lat + 180) - (bounding_box.min_lat + 180)) * 50))
        long_span = int(round(((bounding_box.max_long + 180) - (bounding_box.min_long + 180)) * 50))

        print(lat_span)
        print(long_span)
        #print(self.geometry.loc[(self.geometry["y"] < 90.5) & (self.geometry["y"] > 89.5) & (self.geometry["x"] < 36.5) & (self.geometry["x"] > 35.5)].iloc[0]["Cloud_Top_Height"])
        #print(self.geometry.head())


        layer_frame = pd.DataFrame(columns=["x", "y", "z"])

        for col in layer_frame:
            layer_frame[col] = pd.to_numeric(layer_frame[col], errors='coerce')


        for y in range(0, lat_span):
            for x in range (0, long_span):

                try:
                    z = self.geometry.loc[(self.geometry["x"] < (x + 0.5)) & (self.geometry["x"] > (x - 0.5)) & (self.geometry["y"] < (y + 0.5)) & (self.geometry["y"] > (y - 0.5))].iloc[0]["Cloud_Top_Height"]
                    print("point found")
                except:
                    z = 0

                data = [[x, y ,z]]

                df = pd.DataFrame.from_records(data, columns=["x", "y", "z"])

                layer_frame = pd.concat([layer_frame, df], ignore_index=True)
                print(layer_frame.shape)

        layer_frame["x"] = layer_frame["x"].apply(lambda x: x * 4)
        layer_frame["y"] = layer_frame["y"].apply(lambda x: x * 4)

        #self.plot_plane(layer_frame)

        self.interpolate_plane(layer_frame)

        self.plot_plane(layer_frame)
        self.layer = layer_frame.to_json(orient="records")

        print("writing...")
        layer_frame.to_csv("out.csv")

    def plot_plane(self, layer_frame):
        fig = plt.figure()
        ax = fig.gca(projection='3d')
        ax.plot_trisurf(layer_frame["x"], layer_frame["y"], layer_frame["z"], cmap=plt.cm.viridis, linewidth=0.2)
        plt.show()

    def interpolate_plane(self, layer_frame):
        #print("first dataframe:")
        #print(layer_frame.head(100))
        layer_frame["z"].replace(0, np.nan, inplace=True)
        #f = interpolate.interp2d(layer_frame.x, layer_frame.y, layer_frame.z, kind='linear', fill_value=np.nan)
        # newz = f(np.arange(0, 400, 1), np.arange(0, 400, 1))

        # layer_frame["z"].interpolate(inplace=True, method="akima", axis=0)
        # layer_frame["z"].interpolate(inplace=True, method="akima", axis=1)

        #        xi = yi = np.arange(0, 1600, 4)
        #        xi,yi = np.meshgrid(xi,yi)

        known = layer_frame.loc[layer_frame["z"].notnull()]
        extremeknown = pd.DataFrame([[0,0,0], [400,400,0], [0,400,0], [400,0,0]], columns=list('xyz'))
        #known = pd.concat([known, extremeknown])
        known.dropna(inplace=True)
        #print(known.head())

        knownpoints = known[["x","y"]]
        points = knownpoints.as_matrix()

        #known.to_csv("out.csv")

        x = np.linspace(0, 400, 401)
        y = np.linspace(0, 400, 401)
        X, Y = np.meshgrid(x,y)

        #zi = interpolate.griddata((layer_frame.x.values, layer_frame.y.values), layer_frame.z.values, (xi,yi), method='linear', fill_value=np.nan)
        zi = interpolate.griddata(points, known["z"], (X, Y), method='cubic', fill_value=0)

        #plt.imshow(zi)
        #plt.show()
        #print("X[1]:")
        #print(X[0][0])
       # print("end X[1]")

        #for index, row in layer_frame.iterrows():
            #print(row["x"])
            #row["z"] = zi[int(row["x"])][int(row["y"])]
            #print(row["z"])
            #layer_frame.loc[index, "z"] = zi[int(row["x"])][int(row["y"])]

        layer_frame = pd.DataFrame()


        for xi in x:
            for yi in y:
                data = {"x": xi, "y": yi, "z": zi[int(xi)][int(yi)]}
                #print(xi)
                #print(yi)
                #print(zi[int(xi)][int(yi)])
                layer_frame = pd.concat([layer_frame, pd.DataFrame(data, index=[0])])


        print("finished")

        #for x in range(0,401):
        #    for y in range(0,401):
        #        print("x:" + str(x) + "y:" + str(y))
        #        print(zi[x][y])


        #layer_frame.to_csv("out.csv")
       # print("second dataframe:")
       # print(layer_frame.head(100))
        #self.plot_plane(layer_frame)
