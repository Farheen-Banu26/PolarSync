from typing import List, Tuple, Dict
from ..models.environment import Route, DangerZone
from ..utils.geo import haversine_distance_km, is_inside_danger_zone


class RoutePlanner:
    @staticmethod
    def generate_emergency_route(
        origin_coords: Tuple[float, float],
        destination_coords: Tuple[float, float],
        danger_zones: Dict[str, DangerZone],
        is_aerial: bool = False
    ) -> Route:
        """
        Generate a waypoint sequence from origin to destination.
        If ground-based and path intersects high danger zone, insert a bypass waypoint.
        """
        waypoints = [origin_coords]
        
        # Midpoint
        mid_lat = (origin_coords[0] + destination_coords[0]) / 2.0
        mid_lon = (origin_coords[1] + destination_coords[1]) / 2.0
        mid_point = (round(mid_lat, 6), round(mid_lon, 6))

        terrain_drag = 1.0

        # Check if ground route intersects a ground-blocked danger zone
        if not is_aerial:
            for dz in danger_zones.values():
                if is_inside_danger_zone(mid_point, dz.center_coordinates, dz.radius_km):
                    terrain_drag = 1.5
                    # Offset waypoint to circumvent zone
                    bypass_lat = dz.center_coordinates[0] + (dz.radius_km / 111.0) * 1.2
                    bypass_lon = dz.center_coordinates[1] + (dz.radius_km / 111.0) * 1.2
                    waypoints.append((round(bypass_lat, 6), round(bypass_lon, 6)))
                    break

        waypoints.append(destination_coords)
        
        # Calculate total distance along segments
        total_dist_km = 0.0
        for i in range(len(waypoints) - 1):
            total_dist_km += haversine_distance_km(waypoints[i], waypoints[i+1])

        return Route(
            id=f"EMERGENCY-ROUTE-{len(waypoints)}WP",
            name="Emergency Dispatch Route",
            origin_id="DISPATCH_ORIGIN",
            destination_id="EMERGENCY_LOC",
            waypoints=waypoints,
            distance_km=round(total_dist_km, 2),
            terrain_difficulty=terrain_drag
        )
