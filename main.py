'''
This module helps user to find 10 nearest locations, where
films of given year were filmed. You also can find some helping
functions here.
'''
from math import cos, sin, asin, sqrt, pi
import folium
import geopy
from geopy.extra.rate_limiter import RateLimiter
from geopy.exc import GeocoderUnavailable

def reading (path: str) -> list:
    '''
    Reads file from given path, and returns list of its rows.
    If path is not str returns None
    >>> reading(1)

    '''
    if not isinstance(path, str):
        return None

    read = open(path, 'r')
    lines = read.readlines()
    return lines

def collecting_films_year (year: str, lines: list, number: int, starter: int) -> list:
    '''
    Returns list of films, filmed on given year, from starter-th to starter+number-th.
    If at lest one variable is not of correct type returns None
    >>> collecting_films_year ('','','','')

    '''
    if not isinstance(year, str) or not isinstance(lines, list) or not isinstance(number, int)\
        or not isinstance(starter, int):
        return None

    needed_year = []

    for line in lines:
        if year in line:
            line = line.rstrip().split('\t')

            while line[-1][-1] == ')':
                line.pop()

            needed_year.append(line)
    return needed_year[starter: starter + number]

def haversin (angle:float) -> float:
    '''
    Returns haversinus of given angle(in radians)
    >>> haversin(1)
    0.22984884706593015
    '''
    haver = sin(angle / 2) ** 2
    return haver

def to_radians (angle: float) -> float:
    '''
    Converts angle in degrees to radians
    >>> round(to_radians(180),2)
    3.14
    '''
    return pi*angle/180

def calc_distance(lat1: float, lat2: float, lon1: float, lon2: float) -> float:
    '''
    Returns distance in meters between two points having their latitude and longtitude
    >>> calc_distance(48.3, 48.3, 25.934, 25.934)
    0.0
    '''
    earth_r = 6371000
    lat1, lat2, lon1, lon2 = list(map(to_radians, [lat1, lat2, lon1, lon2]))
    distance = 2 * earth_r * asin(sqrt(haversin(lat1 - lat2) + \
        cos(lat1) * cos(lat2) * haversin(lon1 - lon2)))

    return distance

def found_nearest (lat: float, lon: float, films: list, number: int) -> list:
    '''
    Returns ten nearest film locaions from given list
    '''
    geolocator = geopy.Nominatim (user_agent='my-aplication')
    nearest = []
    locations = {}
    unsuit = set()

    print('Collecting locations started')
    persentage = 0

    for index, film in enumerate(films):
        if (index + 1) * 100//number == persentage:
            print(persentage, '%', ' complete', sep = '')
            persentage += 10

        try:
            if film[-1] not in unsuit:
                if film[-1] not in locations:
                    geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1)
                    location = geolocator.geocode(film[-1])
                    lat1 = location.latitude
                    lon1 = location.longitude
                    dist = calc_distance(lat, lat1, lon, lon1)
                    locations[film[-1]] = [dist, lat1, lon1]

                else:
                    dist = locations[film[-1]][0]
                    lat1 = locations[film[-1]][1]
                    lon1 = locations[film[-1]][2]

                length = len(nearest)

                if length == 0:
                    nearest.append([dist, lat1, lon1, film[0]])
                else:
                    if length < 10:
                        if nearest[-1][0] > dist:
                            for i in range(length):
                                if nearest[i][0] > dist:
                                    nearest.insert(i, [dist, lat1, lon1, film[0]])
                                    break
                        else:
                            nearest.append([dist, lat1, lon1, film[0]])
                    else:
                        if nearest[-1][0] > dist:
                            for i in range(length):
                                if nearest[i][0] > dist:
                                    nearest.insert(i, [dist, lat1, lon1, film[0]])
                                    break
                            nearest.pop()
                        else:
                            unsuit.add(film[-1])

        except AttributeError:
            unsuit.add(film[-1])

        except GeocoderUnavailable:
            unsuit.add(film[-1])
    return nearest

def calculate_midpoints(points, user_loc):
    '''
    Returns locations of midpoints between films and user.
    '''
    middles = []
    for point in points:
        middles.append([(point[1] + user_loc[0]) / 2, (point[2] + user_loc[1]) / 2, point[3]])
    return middles

def generate_map (nearest, midpoints, user_loc, year):
    '''
    Generates needed map
    '''
    my_map = folium.Map (location = user_loc, zoom_start=10)
    fg_films = folium.FeatureGroup(name = year + ' films')

    for film in nearest:
        fg_films.add_child(folium.CircleMarker(location = [film[1], film[2]], radius = 10,\
            popup = film[3], fill_color = 'blue', opacity = 1))

    fg_user = folium.FeatureGroup(name = "Your location")
    fg_user = fg_user.add_child(folium.Marker(location = user_loc, popup = "You are here"))
    fg_mids = folium.FeatureGroup(name='Middle points')

    for point in midpoints:
        fg_mids.add_child(folium.CircleMarker(location = [point[0], point[1]], radius = 4,\
            popup = 'Half of the way to' + point[2], color = 'red', fill_color = 'red', opacity = 1\
                ))

    my_map.add_child(fg_films)
    my_map.add_child(fg_user)
    my_map.add_child(fg_mids)
    my_map.add_child(folium.LayerControl())
    my_map.save('Film_map.html')

if __name__ == "__main__":
    while True:
        try:
            us_year = input("Please enter a year you would like to have a map for: ")
            user = list(map(float, input("Please enter your location (format: lat, long): ").split\
                (', ')))
            start = int(input("Enter starter number of film from which you want to start analyse: "
                ))
            num = int(input("Enter number of films from given list, which you want to analyse \
(note, that for 3000 number it'll take 3-4 minutes, for 10 000 - 10-12 minutes and etc.): "))
            print("Map is generating...")
            al_film = reading('locations.list')
            films = collecting_films_year('(' + us_year + ')', al_film, num, start)
            near = found_nearest(user[0], user[1], films, num)
            mid = calculate_midpoints(near, user)
            generate_map(near, mid, user, us_year)
            print('Map is ready! Open Film_map.html and have fun)')
            break
        except ValueError:
            print('Something went wrong, check your input and try again.')
        except TypeError:
            print('Something went wrong, check your input and try again.')
