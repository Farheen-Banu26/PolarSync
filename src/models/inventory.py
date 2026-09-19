from dataclasses import dataclass
from enum import Enum


class InventoryCategory(str, Enum):
    FOOD = "FOOD"
    FUEL = "FUEL"
    MEDICAL_SUPPLIES = "MEDICAL_SUPPLIES"
    OXYGEN = "OXYGEN"
    SPARE_PARTS = "SPARE_PARTS"


class ResupplyRisk(str, Enum):
    LOW_SAFE = "LOW_SAFE"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class InventoryItem:
    category: InventoryCategory
    location_id: str
    current_stock: float
    unit: str
    daily_consumption_rate: float
    safety_buffer_days: float = 15.0
    next_resupply_window_days: float = 20.0

    @property
    def days_of_autonomy(self) -> float:
        """
        Days of Autonomy = Current Stock / Daily Consumption Rate
        """
        if self.daily_consumption_rate <= 0:
            return 999.0  # infinite/zero consumption
        return round(self.current_stock / self.daily_consumption_rate, 2)

    @property
    def resupply_risk(self) -> ResupplyRisk:
        """
        Calculate resupply risk tier based on Days of Autonomy and resupply schedule.
        """
        doa = self.days_of_autonomy
        window = self.next_resupply_window_days
        buffer = self.safety_buffer_days

        if doa <= window:
            return ResupplyRisk.CRITICAL
        elif doa <= (window + buffer * 0.5):
            return ResupplyRisk.HIGH
        elif doa <= (window + buffer):
            return ResupplyRisk.MODERATE
        else:
            return ResupplyRisk.LOW_SAFE

    def consume(self, delta_days: float):
        """
        Deduct consumption over a fractional or integer day interval.
        """
        deduction = self.daily_consumption_rate * delta_days
        self.current_stock = max(0.0, self.current_stock - deduction)
