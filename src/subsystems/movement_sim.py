import numpy as np
from typing import Dict, Optional, Tuple
from ..models.vehicle import Vehicle, VehicleStatus, VehicleType
from ..models.environment import Route, WeatherState
from ..utils.geo import haversine_distance_km, calculate_bearing_deg, interpolate_position


class MovementSubsystem:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def step(
        self,
        vehicles: Dict[str, Vehicle],
        routes: Dict[str, Route],
        weather: WeatherState,
        delta_hours: float
    ):
        for vehicle in vehicles.values():
            if vehicle.status in (VehicleStatus.IN_TRANSIT, VehicleStatus.DISPATCHED_EMERGENCY):
                self._update_vehicle_in_transit(vehicle, routes, weather, delta_hours)
            elif vehicle.status == VehicleStatus.AVAILABLE:
                # Stationary/Idle mechanics
                self._update_vehicle_idle(vehicle, weather, delta_hours)

    def _update_vehicle_in_transit(
        self,
        vehicle: Vehicle,
        routes: Dict[str, Route],
        weather: WeatherState,
        delta_hours: float
    ):
        route = routes.get(vehicle.current_route_id) if vehicle.current_route_id else None
        if not route or len(route.waypoints) < 2:
            # No valid route, stop vehicle
            vehicle.speed_kmh = 0.0
            return

        # Base nominal speeds by type
        nominal_speeds = {
            VehicleType.HELICOPTER: 180.0,
            VehicleType.SKIDOO: 45.0,
            VehicleType.SNOWCAT: 25.0,
            VehicleType.PISTON_BULLY: 20.0
        }
        base_speed = nominal_speeds.get(vehicle.vehicle_type, 30.0)

        # Weather & terrain drag penalty
        weather_drag = 1.0 - min(0.5, (weather.wind_speed_kmh / 100.0) * 0.4)
        terrain_drag = 1.0 / max(1.0, route.terrain_difficulty)
        
        # Add slight realistic noise
        speed_jitter = float(self.rng.normal(0.0, 1.0))
        target_speed = max(5.0, (base_speed * weather_drag * terrain_drag) + speed_jitter)
        vehicle.speed_kmh = round(target_speed, 1)

        # Calculate distance covered in this timestep
        dist_covered_km = vehicle.speed_kmh * delta_hours
        
        # Advance progress along waypoints
        total_route_dist = route.distance_km if route.distance_km > 0 else 1.0
        progress_delta = (dist_covered_km / total_route_dist) * 100.0
        vehicle.route_progress_pct = min(100.0, vehicle.route_progress_pct + progress_delta)

        # Determine waypoint segment
        num_segments = len(route.waypoints) - 1
        if num_segments > 0:
            segment_fraction = vehicle.route_progress_pct / 100.0
            segment_idx = min(num_segments - 1, int(segment_fraction * num_segments))
            sub_fraction = (segment_fraction * num_segments) - segment_idx

            p1 = route.waypoints[segment_idx]
            p2 = route.waypoints[segment_idx + 1]

            vehicle.position = interpolate_position(p1, p2, min(1.0, max(0.0, sub_fraction)))
            vehicle.heading_deg = round(calculate_bearing_deg(p1, p2), 1)

        # Fuel burn
        fuel_used = dist_covered_km * vehicle.fuel_burn_rate_l_per_km * route.terrain_difficulty
        vehicle.fuel_level_l = max(0.0, round(vehicle.fuel_level_l - fuel_used, 2))

        # Battery drain
        vehicle.battery_level_pct = max(0.0, round(vehicle.battery_level_pct - (0.5 * delta_hours), 2))

        # Engine temperature
        target_engine_temp = 80.0 if vehicle.vehicle_type != VehicleType.HELICOPTER else 95.0
        vehicle.engine_temp_c = round(target_engine_temp + float(self.rng.normal(0, 0.5)), 1)

        # Check for destination arrival
        if vehicle.route_progress_pct >= 100.0:
            vehicle.speed_kmh = 0.0
            vehicle.route_progress_pct = 100.0
            if vehicle.status == VehicleStatus.DISPATCHED_EMERGENCY:
                # Arrived at emergency site
                pass  # handover to SAR coordinator
            else:
                vehicle.status = VehicleStatus.AVAILABLE
                vehicle.current_route_id = None

    def _update_vehicle_idle(self, vehicle: Vehicle, weather: WeatherState, delta_hours: float):
        vehicle.speed_kmh = 0.0
        # Engine cools down toward ambient if turned off, or stays warm if idling
        target_temp = weather.ambient_temp_c + 15.0  # block heater / passive warming
        vehicle.engine_temp_c = round(
            vehicle.engine_temp_c + (target_temp - vehicle.engine_temp_c) * 0.1 * delta_hours, 1
        )
