from dataclasses import dataclass
from enum import Enum
from typing import Tuple, Optional


class CargoCategory(str, Enum):
    MEDICAL_SAMPLES = "MEDICAL_SAMPLES"
    PERISHABLE_FOOD = "PERISHABLE_FOOD"
    SCIENTIFIC_EQUIPMENT = "SCIENTIFIC_EQUIPMENT"
    SPARE_PARTS = "SPARE_PARTS"
    HAZMAT_FUEL = "HAZMAT_FUEL"


class CargoLifecycleStage(str, Enum):
    PACKED = "PACKED"
    QC = "QC"
    LOADED = "LOADED"
    IN_TRANSIT = "IN_TRANSIT"
    ARRIVED = "ARRIVED"
    INSPECTED = "INSPECTED"
    DELIVERED = "DELIVERED"


class CargoCondition(str, Enum):
    NOMINAL = "NOMINAL"
    WARNING_DRIFT = "WARNING_DRIFT"
    BREACHED_DAMAGED = "BREACHED_DAMAGED"


@dataclass
class CargoItem:
    id: str
    name: str
    category: CargoCategory
    weight_kg: float
    origin_id: str
    destination_id: str
    lifecycle_stage: CargoLifecycleStage = CargoLifecycleStage.PACKED
    carrier_vehicle_id: Optional[str] = None
    current_coordinates: Tuple[float, float] = (0.0, 0.0)
    is_temperature_sensitive: bool = False
    min_temp_c: float = -30.0
    max_temp_c: float = -10.0
    current_temp_c: float = -20.0
    condition: CargoCondition = CargoCondition.NOMINAL
    cooling_active: bool = True
    insulation_factor: float = 0.95  # resistance to ambient drift

    def check_thermal_status(self) -> CargoCondition:
        if not self.is_temperature_sensitive:
            self.condition = CargoCondition.NOMINAL
            return self.condition

        if self.current_temp_c < self.min_temp_c or self.current_temp_c > self.max_temp_c:
            self.condition = CargoCondition.BREACHED_DAMAGED
        elif (self.current_temp_c > self.max_temp_c - 2.0) or (self.current_temp_c < self.min_temp_c + 2.0):
            self.condition = CargoCondition.WARNING_DRIFT
        else:
            self.condition = CargoCondition.NOMINAL
        return self.condition

    def advance_stage(self) -> CargoLifecycleStage:
        order = [
            CargoLifecycleStage.PACKED,
            CargoLifecycleStage.QC,
            CargoLifecycleStage.LOADED,
            CargoLifecycleStage.IN_TRANSIT,
            CargoLifecycleStage.ARRIVED,
            CargoLifecycleStage.INSPECTED,
            CargoLifecycleStage.DELIVERED
        ]
        curr_idx = order.index(self.lifecycle_stage)
        if curr_idx < len(order) - 1:
            self.lifecycle_stage = order[curr_idx + 1]
        return self.lifecycle_stage
