import math


def take_angle(element):
    return element['angle']


def sort_coordinates(corner_list):
    midpoint = get_midpoint(corner_list)

    corner_metadata = []

    for corner in corner_list:
        angle = get_angle(corner, midpoint)
        corner_metadata.append({'corner': corner, 'angle': angle})


    #print(corner_metadata)
    corner_metadata = sorted(corner_metadata, key = lambda x: x['angle']) #sort by angle
    #print('test list:', test_list)

    sorted_corner_list = []

    for meta in corner_metadata:
        sorted_corner_list.append(meta['corner'])

    return sorted_corner_list

def get_angle(point, midpoint):
    dX = point['long'] - midpoint['long']
    dY = point['lat'] - midpoint['lat']
    rads = math.atan2 (-dY, dX)
    rads = rads - (math.pi / 2)
    return rads

def get_midpoint(corner_list):

    lat_list = []
    long_list = []

    for corner in corner_list:
        lat_list.append(corner['lat'])
        long_list.append(corner['long'])

    return {'lat': sum(lat_list)/len(lat_list),'long': sum(long_list)/len(long_list)}



def bounding_box_within_swath(swath_box, select_box):

    match_1 = False
    match_2 = False
    match_3 = False
    match_4 = False

    if point_east_of_bound(swath_box.corners[0]['long'], select_box.corners[0]['long']):
        if point_south_of_bound(swath_box.corners[0]['lat'], select_box.corners[0]['lat']):
            match_1 = True


    if point_west_of_bound(swath_box.corners[1]['long'], select_box.corners[1]['long']):
        if point_south_of_bound(swath_box.corners[1]['lat'], select_box.corners[1]['lat']):
            match_2 = True

    if point_west_of_bound(swath_box.corners[2]['long'], select_box.corners[2]['long']):
        if point_north_of_bound(swath_box.corners[2]['lat'], select_box.corners[2]['lat']):
            match_3 = True

    if point_east_of_bound(swath_box.corners[3]['long'], select_box.corners[3]['long']):
        if point_north_of_bound(swath_box.corners[3]['lat'], select_box.corners[3]['lat']):
            match_4 = True

    #print(match_1)
    #print(match_2)
    #print(match_3)
    #print(match_4)

    if int(swath_box.corners[0]['long']) == -148:
        print('box found!!!')

        swath_box.print_geometries()

        print(point_east_of_bound(swath_box.corners[0]['long'], select_box.corners[0]['long']))
        print(point_south_of_bound(swath_box.corners[0]['lat'], select_box.corners[0]['lat']))


        print(point_west_of_bound(swath_box.corners[1]['long'], select_box.corners[1]['long']))
        print(point_south_of_bound(swath_box.corners[1]['lat'], select_box.corners[1]['lat']))

        print(point_east_of_bound(swath_box.corners[2]['long'], select_box.corners[2]['long']))
        print(point_north_of_bound(swath_box.corners[2]['lat'], select_box.corners[2]['lat']))

        print(point_west_of_bound(swath_box.corners[3]['long'], select_box.corners[3]['long']))
        print(point_north_of_bound(swath_box.corners[3]['lat'], select_box.corners[3]['lat']))


        #print( swath_box.corners[0]['long'])
        #print(select_box.corners[0]['long'])


    if match_1 and match_2 and match_3 and match_4:

        print(point_east_of_bound(swath_box.corners[0]['long'], select_box.corners[0]['long']))
        print( swath_box.corners[0]['long'])
        print(select_box.corners[0]['long'])

        return True


    return False


def point_east_of_bound(swath_long, select_long):
    if select_long > 90 and swath_long < -90:
        swath_long = swath_long + 180
        select_long = select_long - 180
        if swath_long < select_long:
            return True
    else:
        if swath_long < select_long:
            return True

    return False

def point_west_of_bound(swath_long, select_long):
    if select_long > 90 and swath_long < -90:
        swath_long = swath_long + 180
        select_long = select_long - 180
        if swath_long > select_long:
            return True
    else:
        if swath_long > select_long:
            return True

    return False


def point_north_of_bound(swath_lat, select_lat):
    if swath_lat < select_lat:
        return True
    return False

def point_south_of_bound(swath_lat, select_lat):
     if swath_lat > select_lat:
        return True
     return False



#determinant of matrix a
def det(a):
    return a[0][0]*a[1][1]*a[2][2] + a[0][1]*a[1][2]*a[2][0] + a[0][2]*a[1][0]*a[2][1] - a[0][2]*a[1][1]*a[2][0] - a[0][1]*a[1][0]*a[2][2] - a[0][0]*a[1][2]*a[2][1]

#unit normal vector of plane defined by points a, b, and c
def unit_normal(a, b, c):
    x = det([[1,a[1],a[2]],
             [1,b[1],b[2]],
             [1,c[1],c[2]]])
    y = det([[a[0],1,a[2]],
             [b[0],1,b[2]],
             [c[0],1,c[2]]])
    z = det([[a[0],a[1],1],
             [b[0],b[1],1],
             [c[0],c[1],1]])
    magnitude = (x**2 + y**2 + z**2)**.5
    return (x/magnitude, y/magnitude, z/magnitude)

#dot product of vectors a and b
def dot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

#cross product of vectors a and b
def cross(a, b):
    x = a[1] * b[2] - a[2] * b[1]
    y = a[2] * b[0] - a[0] * b[2]
    z = a[0] * b[1] - a[1] * b[0]
    return (x, y, z)

#area of polygon poly
def area(poly):
    if len(poly) < 3: # not a plane - no area
        return 0

    total = [0, 0, 0]
    for i in range(len(poly)):
        vi1 = poly[i]
        if i is len(poly)-1:
            vi2 = poly[0]
        else:
            vi2 = poly[i+1]
        prod = cross(vi1, vi2)
        total[0] += prod[0]
        total[1] += prod[1]
        total[2] += prod[2]
    result = dot(total, unit_normal(poly[0], poly[1], poly[2]))
    return abs(result/2)
