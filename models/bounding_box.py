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



