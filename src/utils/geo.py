import math
from typing import Tuple, List

EARTH_RADIUS_KM = 6371.0


def haversine_distance_km(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate the great-circle distance between two points on the Earth's surface (in km).
    coord: (latitude, longitude) in decimal degrees.
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    return EARTH_RADIUS_KM * c


def calculate_bearing_deg(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """
    Calculate initial compass bearing from coord1 to coord2 in degrees [0, 360).
    """
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])

    delta_lon = lon2 - lon1
    x = math.sin(delta_lon) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon))

    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360

    return compass_bearing


def interpolate_position(coord1: Tuple[float, float], coord2: Tuple[float, float], fraction: float) -> Tuple[float, float]:
    """
    Linearly interpolate between two coordinates by a given fraction [0.0, 1.0].
    """
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    interp_lat = lat1 + (lat2 - lat1) * fraction
    interp_lon = lon1 + (lon2 - lon1) * fraction
    return (round(interp_lat, 6), round(interp_lon, 6))


def is_inside_danger_zone(point: Tuple[float, float], zone_center: Tuple[float, float], radius_km: float) -> bool:
    """
    Check if a coordinate point falls inside a danger zone defined by center and radius.
    """
    dist = haversine_distance_km(point, zone_center)
    return dist <= radius_km
