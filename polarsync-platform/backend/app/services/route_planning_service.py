"""
PolarSync Route Planning & Validation Engine
Calculates geodesic distances, waypoint trajectories, vehicle fuel autonomy feasibility, and danger zone intersections.
SIH Problem Statement: SIH26062
"""
import math
from typing import List, Dict, Any, Tuple


class RoutePlanningService:
    @staticmethod
    def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate geodesic distance between two Antarctic coordinate points in kilometers.
        """
        r = 6371.0  # Earth radius in km
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return round(r * c, 2)

    def calculate_route_metrics(
        self,
        origin_coords: List[float],
        destination_coords: List[float],
        waypoints: List[List[float]],
        avg_speed_kmh: float = 18.0,
        fuel_consumption_l_per_km: float = 1.4,
        vehicle_fuel_capacity_l: float = 450.0,
        current_fuel_pct: float = 100.0,
        danger_zones: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculates total traverse distance, expected travel time, fuel consumed, fuel remaining,
        and proximity/intersection with active danger zones (crevasses, blue ice, severe wind corridors).
        """
        all_points = [origin_coords] + (waypoints or []) + [destination_coords]
        
        total_distance_km = 0.0
        segments = []
        for i in range(len(all_points) - 1):
            p1 = all_points[i]
            p2 = all_points[i + 1]
            seg_dist = self.haversine_distance_km(p1[0], p1[1], p2[0], p2[1])
            total_distance_km += seg_dist
            segments.append({
                "from_index": i,
                "to_index": i + 1,
                "distance_km": seg_dist
            })

        total_distance_km = round(total_distance_km, 2)
        travel_time_hours = round(total_distance_km / max(avg_speed_kmh, 1.0), 2)
        
        fuel_needed_liters = round(total_distance_km * fuel_consumption_l_per_km, 1)
        current_fuel_liters = (current_fuel_pct / 100.0) * vehicle_fuel_capacity_l
        remaining_fuel_liters = round(current_fuel_liters - fuel_needed_liters, 1)
        remaining_fuel_pct = round((remaining_fuel_liters / vehicle_fuel_capacity_l) * 100.0, 1) if vehicle_fuel_capacity_l > 0 else 0.0

        is_fuel_feasible = remaining_fuel_liters >= (0.15 * vehicle_fuel_capacity_l)  # 15% safety reserve required in Antarctica

        # Check danger zones proximity
        intersected_hazards = []
        if danger_zones:
            for dz in danger_zones:
                center_lat = dz.get("center_coordinates", [0, 0])[0] if "center_coordinates" in dz else dz.get("center_lat", 0)
                center_lon = dz.get("center_coordinates", [0, 0])[1] if "center_coordinates" in dz else dz.get("center_lon", 0)
                radius_km = dz.get("radius_km", 3.5)

                for pt in all_points:
                    dist_to_hazard = self.haversine_distance_km(pt[0], pt[1], center_lat, center_lon)
                    if dist_to_hazard <= radius_km + 1.5:  # Proximity buffer
                        intersected_hazards.append({
                            "hazard_id": dz.get("id"),
                            "name": dz.get("name"),
                            "type": dz.get("type"),
                            "severity": dz.get("severity"),
                            "distance_to_corridor_km": round(dist_to_hazard, 2)
                        })
                        break

        risk_level = "LOW"
        if not is_fuel_feasible:
            risk_level = "CRITICAL"
        elif intersected_hazards:
            risk_level = "HIGH" if any(h["severity"] == "CRITICAL" for h in intersected_hazards) else "MEDIUM"

        return {
            "total_distance_km": total_distance_km,
            "estimated_travel_time_hours": travel_time_hours,
            "fuel_required_liters": fuel_needed_liters,
            "fuel_remaining_liters": remaining_fuel_liters,
            "fuel_remaining_pct": max(0.0, remaining_fuel_pct),
            "is_fuel_feasible": is_fuel_feasible,
            "risk_level": risk_level,
            "hazard_warnings": intersected_hazards,
            "validation_status": "APPROVED" if (is_fuel_feasible and risk_level != "CRITICAL") else "REQUIRES_OVERRIDE",
            "waypoints": all_points
        }


route_planning_service = RoutePlanningService()
