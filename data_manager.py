import pandas as pd
import datetime as dt
import pyhdf.SD as hdf
import os
import geoutils as gu


class SwathTile:
    def __init__(self, bounding_box, file_path, timestamp):
         self.bounding_box = bounding_box
         self.file_path = file_path
         self.timestamp = timestamp

    def get_dataframe(self, data_type):
        data_file = hdf.SD(self.file_path, hdf.SDC.READ)
        #lat_data = pd.DataFrame(data_file.select('Latitude').get())
        #long_data = pd.DataFrame(data_file.select('Longitude').get())
        variable_data = pd.DataFrame(data_file.select(data_type).get())
        return variable_data


class BoundingBox:

    def __init__(self, corner_1, corner_2, corner_3, corner_4):
        self.corners = []
        self.corners.append(corner_1)
        self.corners.append(corner_2)
        self.corners.append(corner_3)
        self.corners.append(corner_4)

    def print_geometries(self):
        for corner in self.corners:
            print(*list(corner.values()))


#Data management logic
class SwathTileManager:

    swath_tile_list = []

    def get_bounding_box(self, latitude_dataframe, longitude_dataframe):
        corner_1 = {'lat': latitude_dataframe.iloc[0,0], 'long': longitude_dataframe.iloc[0,0]}
        corner_2 = {'lat': latitude_dataframe.iloc[0,-1], 'long': longitude_dataframe.iloc[0,-1]}
        corner_3 = {'lat': latitude_dataframe.iloc[-1,0], 'long': longitude_dataframe.iloc[-1,0]}
        corner_4 = {'lat': latitude_dataframe.iloc[-1,-1], 'long': longitude_dataframe.iloc[-1,-1]}
        bounding_box = BoundingBox(corner_1, corner_2, corner_3, corner_4)
        return bounding_box

    def build_swath_tile(self, file_path):
        data_file = hdf.SD(file_path, hdf.SDC.READ)
        lat_data = pd.DataFrame(data_file.select('Latitude').get())
        long_data = pd.DataFrame(data_file.select('Longitude').get())
        bounding_box = self.get_bounding_box(lat_data, long_data)
        swath_tile = SwathTile(bounding_box, file_path, dt.datetime.now())
        self.swath_tile_list.append(swath_tile)
        if len(self.swath_tile_list) > 3:
            del self.swath_tile_list[0]
        self.update_merged_swath_bounds(self.swath_tile_list)
        self.merged_swath_bounds.print_geometries()

    def update_merged_swath_bounds(self, swath_tile_list):
        direction = self.direction_of_travel(self.swath_tile_list)

        if direction == 'N':
            north_tile_index = len(swath_tile_list) - 1
            south_tile_index = 0
        if direction == 'S':
            north_tile_index = 0
            south_tile_index = len(swath_tile_list) - 1

        corner_1 = {'lat': swath_tile_list[north_tile_index].bounding_box.corners[0]['lat'], 'long': swath_tile_list[north_tile_index].bounding_box.corners[0]['long']}
        corner_2 = {'lat': swath_tile_list[north_tile_index].bounding_box.corners[1]['lat'], 'long': swath_tile_list[north_tile_index].bounding_box.corners[1]['long']}
        corner_3 = {'lat': swath_tile_list[south_tile_index].bounding_box.corners[2]['lat'], 'long': swath_tile_list[south_tile_index].bounding_box.corners[2]['long']}
        corner_4 = {'lat': swath_tile_list[south_tile_index].bounding_box.corners[3]['lat'], 'long': swath_tile_list[south_tile_index].bounding_box.corners[3]['long']}

        self.merged_swath_bounds = BoundingBox(corner_1, corner_2, corner_3, corner_4)

    def direction_of_travel(self, swath_tile_list):
        oldest_lat = swath_tile_list[0].bounding_box.corners[0]['lat']
        youngest_lat = swath_tile_list[len(swath_tile_list) - 1].bounding_box.corners[0]['lat']

        if gu.point_south_of_bound(oldest_lat, youngest_lat):
            return 'S'
        else:
            return 'N'

    def get_merged_swath_dataframe(self, data_type):
        merged_dataframe = pd.DataFrame()

        for tile in self.swath_tile_list:
            merged_dataframe = pd.concat([merged_dataframe, tile.get_dataframe(data_type)])

        return merged_dataframe


#End data management logic


#class SwathTileExporter:
#    def get_data(self, bounding_box, data_type):
#        for geom in manager.swath_tile_list:

swath_manager = SwathTileManager()
#x = DataFetcher()
directory = os.fsencode("/media/joe/DATA/weather_data/test/")


test_box = BoundingBox({'lat':-34,'long':145},{'lat':-34,'long':148},{'lat':-38,'long':145},{'lat':-38,'long':149})


for file in os.listdir(directory):
    filename = os.fsdecode(directory) + os.fsdecode(file)
    swath_manager.build_swath_tile(filename)
    print(gu.bounding_box_within_swath(swath_manager.merged_swath_bounds,test_box))
    print(swath_manager.get_merged_swath_dataframe("Cloud_Top_Height").shape)


#print(point_south_of_bound(20,0)) #True
#print(point_west_of_bound(20,0)) #True


#for swath in swath_tile_list:
#    if bounding_box_within_swath(swath.bounding_box,test_box):



#for tile in manager.swath_tile_list:
#    print(tile.bounding_box)
#    print(tile.file_path)
#    print(tile.timestamp)
#    print("\n")


#print(x.get_latest_file_url())
#x.download_latest_file()
