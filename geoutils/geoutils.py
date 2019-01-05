import math
import pyproj as proj
import shapely.geometry as geometry
from shapely.ops import cascaded_union, polygonize
from scipy.spatial import Delaunay
import numpy as np
import math
from sympy import Point, Polygon, pi

def alpha_shape(points, alpha):
    """
    Compute the alpha shape (concave hull) of a set
    of points.
    @param points: Iterable container of points.
    @param alpha: alpha value to influence the
        gooeyness of the border. Smaller numbers
        don't fall inward as much as larger numbers.
        Too large, and you lose everything!
    """


    coords = np.array(points)

    if len(points) < 4:
        # When you have a triangle, there is no sense
        # in computing an alpha shape.
        return geometry.MultiPoint(list(points)).convex_hull

    def add_edge(edges, edge_points, coords, i, j):
        """
        Add a line between the i-th and j-th points,
        if not in the list already
        """
        if (i, j) in edges or (j, i) in edges:
            # already added
            return

        edges.add( (i, j) )
        edge_points.append(coords[ [i, j] ])

    #coords = np.array([point.coords[0] for point in points])



    tri = Delaunay(coords)
    edges = set()
    edge_points = []
    # loop over triangles:
    # ia, ib, ic = indices of corner points of the
    # triangle
    for ia, ib, ic in tri.vertices:
        pa = coords[ia]
        pb = coords[ib]
        pc = coords[ic]
        # Lengths of sides of triangle
        a = math.sqrt((pa[0]-pb[0])**2 + (pa[1]-pb[1])**2)
        b = math.sqrt((pb[0]-pc[0])**2 + (pb[1]-pc[1])**2)
        c = math.sqrt((pc[0]-pa[0])**2 + (pc[1]-pa[1])**2)
        # Semiperimeter of triangle
        s = (a + b + c)/2.0
        # Area of triangle by Heron's formula
        area = math.sqrt(s*(s-a)*(s-b)*(s-c))
        circum_r = a*b*c/(4.0*area)
        # Here's the radius filter.
        #print circum_r
        if circum_r < 1.0/alpha:
            add_edge(edges, edge_points, coords, ia, ib)
            add_edge(edges, edge_points, coords, ib, ic)
            add_edge(edges, edge_points, coords, ic, ia)
    m = geometry.MultiLineString(edge_points)
    triangles = list(polygonize(m))

    union = cascaded_union(triangles)
    union_coords = []

    for geom in union.geoms:
        #print(geom.exterior.xy)
        #union_coords.extend(geom.exterior.xy)
        exterior = geom.exterior.xy
        x, y = exterior[0], exterior[1]
        for i in range(len(x)):
            union_coords.append((x[i],y[i]))

    test = geometry.Polygon(union_coords)

    return test


def concave_hull(points, alpha, delunay_args=None):
    """Computes the concave hull (alpha-shape) of a set of points.
    """
    delunay_args = delunay_args or {
        'furthest_site': False,
        'incremental': False,
        'qhull_options': None
    }
    triangulation = Delaunay(np.array(points))
    alpha_complex = get_alpha_complex(alpha, points, triangulation.simplices)


    X, Y = [], []
    for s in triangulation.simplices:
        X.append([points[s[k]][0] for k in [0, 1, 2, 0]])
        Y.append([points[s[k]][1] for k in [0, 1, 2, 0]])
    poly = geometry.Polygon(list(zip(X[0], Y[0])))
    for i in range(1, len(X)):
        poly = poly.union(geometry.Polygon(list(zip(X[i], Y[i]))))
    return poly

def get_alpha_complex(alpha, points, simplexes):
    """Obtain the alpha shape.
    Args:
        alpha (float): the paramter for the alpha shape
        points: data points
        simplexes: the list of indices that define 2-simplexes in the Delaunay
            triangulation
    """
    return filter(lambda simplex: circumcircle(points, simplex)[1] < alpha, simplexes)

def circumcircle(points, simplex):
    """Computes the circumcentre and circumradius of a triangle:
    https://en.wikipedia.org/wiki/Circumscribed_circle#Circumcircle_equations
    """
    A = [points[simplex[k]] for k in range(3)]
    M = np.asarray(
        [[1.0] * 4] +
        [[sq_norm(A[k]), A[k][0], A[k][1], 1.0] for k in range(3)],
        dtype=np.float32)
    S = np.array([
        0.5 * np.linalg.det(M[1:, [0, 2, 3]]),
        -0.5 * np.linalg.det(M[1:, [0, 1, 3]])
    ])
    a = np.linalg.det(M[1:, 1:])
    b = np.linalg.det(M[1:, [0, 1, 2]])
    centre, radius = S / a, np.sqrt(b / a + sq_norm(S) / a**2)
    return centre, radius


def project(self, row):
    x2,y2 = proj.transform(in_projection, out_projection, row['long'], row['lat'])

    return pd.Series([x2, y2])


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
    dX = point[0] - midpoint[0]
    dY = point[1] - midpoint[1]
    rads = math.atan2 (-dY, dX)
    rads = rads - (math.pi / 2)
    return rads

def get_midpoint(corner_list):

    lat_list = []
    long_list = []

    for corner in corner_list:
        lat_list.append(corner[1])
        long_list.append(corner[0])

    return (sum(long_list)/len(long_list), sum(lat_list)/len(lat_list))



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

    if int(swath_box.corners[0]['long']) == -166:
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

def polygon_contain(swath_box, select_box):
    sw1, sw2, sw3, sw4 = [(swath_box.corners[0]['lat'], swath_box.corners[0]['long']), (swath_box.corners[1]['lat'], swath_box.corners[1]['long']), (swath_box.corners[2]['lat'], swath_box.corners[2]['long']), (swath_box.corners[3]['lat'], swath_box.corners[3]['long'])]
    se1, se2, se3, se4 = [(select_box.corners[0]['lat'], select_box.corners[0]['long']), (select_box.corners[1]['lat'], select_box.corners[1]['long']), (select_box.corners[2]['lat'], select_box.corners[2]['long']), (select_box.corners[3]['lat'], select_box.corners[3]['long'])]

    swath_poly = Polygon(sw1, sw2, sw3, sw4)
    select_poly = Polygon(se1, se2, se3, se4)

    print(swath_poly.encloses(select_poly))
    return swath_poly.encloses(select_poly)

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
