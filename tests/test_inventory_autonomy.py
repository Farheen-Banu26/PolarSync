import pytest
from src.models.inventory import InventoryItem, InventoryCategory, ResupplyRisk


def test_days_of_autonomy_calculation():
    # 18,000 Liters / 600 Liters per day = 30 Days
    fuel = InventoryItem(
        category=InventoryCategory.FUEL,
        location_id="BASE-MAITRI",
        current_stock=18000.0,
        unit="LITERS",
        daily_consumption_rate=600.0,
        safety_buffer_days=15.0,
        next_resupply_window_days=14.0
    )
    assert fuel.days_of_autonomy == 30.0
    assert fuel.resupply_risk == ResupplyRisk.LOW_SAFE


def test_resupply_risk_transitions():
    # Next resupply window = 14 days, safety buffer = 15 days
    # Critical if <= 14 days
    item = InventoryItem(
        category=InventoryCategory.FOOD,
        location_id="BASE-MAITRI",
        current_stock=1400.0,
        unit="RATIONS",
        daily_consumption_rate=100.0,
        safety_buffer_days=15.0,
        next_resupply_window_days=14.0
    )
    assert item.days_of_autonomy == 14.0
    assert item.resupply_risk == ResupplyRisk.CRITICAL

    # High if <= 14 + 7.5 = 21.5 days
    item.current_stock = 1800.0
    assert item.days_of_autonomy == 18.0
    assert item.resupply_risk == ResupplyRisk.HIGH

    # Moderate if <= 14 + 15 = 29 days
    item.current_stock = 2500.0
    assert item.days_of_autonomy == 25.0
    assert item.resupply_risk == ResupplyRisk.MODERATE

    # Safe if > 29 days
    item.current_stock = 3500.0
    assert item.days_of_autonomy == 35.0
    assert item.resupply_risk == ResupplyRisk.LOW_SAFE
