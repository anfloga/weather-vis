import datetime as dt
from shapely.geometry import shape, Point, mapping, Polygon, box




class Query:
    def __init__(self, request):
        body = request.get_json()
        features = body['features']

        self.query_shape = shape(features[0]['geometry'])
        self.projected_shape = self.__project__(self.query_shape)

    def __project__(self, shape):
        l_long = shape.bounds[0]
        u_long = shape.bounds[2]

        l_lat = shape.bounds[1]
        u_lat = shape.bounds[3]

        if l_long < 0:
            l_long = l_long + 360

        if u_long < 0:
            u_long = u_long + 360

        return box(l_long, l_lat, u_long, u_lat)
