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

    if point_east_of_bound(swath_box.corners[2]['long'], select_box.corners[2]['long']):
        if point_north_of_bound(swath_box.corners[2]['lat'], select_box.corners[2]['lat']):
            match_3 = True

    if point_west_of_bound(swath_box.corners[3]['long'], select_box.corners[3]['long']):
        if point_north_of_bound(swath_box.corners[3]['lat'], select_box.corners[3]['lat']):
            match_4 = True

    if match_1 and match_2 and match_3 and match_4:
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
