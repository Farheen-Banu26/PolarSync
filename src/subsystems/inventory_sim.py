from typing import Dict
from ..models.inventory import InventoryItem


class InventorySubsystem:
    def step(
        self,
        inventory: Dict[str, InventoryItem],
        delta_days: float
    ):
        for item in inventory.values():
            item.consume(delta_days)
