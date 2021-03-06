import pandas as pd
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
        merged_stack["x"] = merged_stack["lat"].apply(lambda x: (x - bounding_box.min_lat) * 100)
        merged_stack["y"] = merged_stack["long"].apply(lambda x: (x - bounding_box.min_long) * 100)
        return merged_stack

    def get_local_point(self, minimum, point):
        #1 deg = 100 px
        #if minimum < 0 && point < 0:
        #    return (point - minimum)

        #if minimum < 0 && point > 0:
        #    return (point - minimum)
        return (point - minimum) * 100

