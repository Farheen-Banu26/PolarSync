import numpy as np
from typing import Dict
from ..models.cargo import CargoItem, CargoLifecycleStage, CargoCondition
from ..models.vehicle import Vehicle
from ..models.environment import WeatherState


class CargoSubsystem:
    def __init__(self, rng: np.random.Generator):
        self.rng = rng

    def step(
        self,
        cargo_items: Dict[str, CargoItem],
        vehicles: Dict[str, Vehicle],
        weather: WeatherState,
        delta_hours: float
    ):
        for cargo in cargo_items.values():
            # Update location and lifecycle stage if carrier vehicle exists
            if cargo.carrier_vehicle_id and cargo.carrier_vehicle_id in vehicles:
                veh = vehicles[cargo.carrier_vehicle_id]
                cargo.current_coordinates = veh.position
                
                if veh.status.value in ("IN_TRANSIT", "DISPATCHED_EMERGENCY"):
                    cargo.lifecycle_stage = CargoLifecycleStage.IN_TRANSIT
                elif veh.route_progress_pct >= 100.0:
                    if cargo.lifecycle_stage == CargoLifecycleStage.IN_TRANSIT:
                        cargo.lifecycle_stage = CargoLifecycleStage.ARRIVED
                    elif cargo.lifecycle_stage == CargoLifecycleStage.ARRIVED:
                        cargo.lifecycle_stage = CargoLifecycleStage.INSPECTED
                    elif cargo.lifecycle_stage == CargoLifecycleStage.INSPECTED:
                        cargo.lifecycle_stage = CargoLifecycleStage.DELIVERED

            # Thermal physics simulation for sensitive cargo
            if cargo.is_temperature_sensitive:
                self._update_thermal_state(cargo, weather, delta_hours)

    def _update_thermal_state(
        self,
        cargo: CargoItem,
        weather: WeatherState,
        delta_hours: float
    ):
        target_cooling_temp = (cargo.min_temp_c + cargo.max_temp_c) / 2.0
        
        if cargo.cooling_active:
            # Active refrigeration maintaining nominal target
            drift_rate = 0.5 * delta_hours
            jitter = float(self.rng.normal(0.0, 0.05))
            cargo.current_temp_c += (target_cooling_temp - cargo.current_temp_c) * drift_rate + jitter
        else:
            # Cooling unit failed: drift towards ambient temperature
            insulation_resistance = max(0.05, cargo.insulation_factor)
            heat_leak_rate = (1.0 - insulation_resistance) * 4.0 * delta_hours
            cargo.current_temp_c += (weather.ambient_temp_c - cargo.current_temp_c) * heat_leak_rate

        cargo.current_temp_c = round(cargo.current_temp_c, 2)
        cargo.check_thermal_status()
