"""
PolarSync Database Models & Transaction Integrity Verification Suite
SIH Problem Statement: SIH26062
"""
import os
import sys
import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in python path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.session import Base, check_db_connection
from app.db.models import (
    User,
    Expedition,
    Route,
    CargoItem,
    InventoryRecord,
    PersonnelMember,
    AssetVehicle,
    EmergencyIncident,
    AlertRecord,
    AuditLog
)


@pytest.fixture(scope="module")
def db_session():
    """Create an isolated in-memory test database and session."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_database_table_creation(db_session):
    """Verify all 10 required entity tables exist in metadata."""
    tables = Base.metadata.tables.keys()
    required = [
        "users",
        "expeditions",
        "routes",
        "cargo_items",
        "inventory_records",
        "personnel_members",
        "asset_vehicles",
        "emergency_incidents",
        "alert_records",
        "audit_logs"
    ]
    for table in required:
        assert table in tables, f"Table {table} missing from SQLAlchemy metadata"


def test_user_crud(db_session):
    """Verify User model CRUD and constraints."""
    user = User(
        username="commander_test",
        hashed_password="hashed_secret",
        role="Expedition Commander",
        full_name="Dr. Rajesh Sharma",
        email="rajesh.test@ncpor.gov.in"
    )
    db_session.add(user)
    db_session.commit()

    fetched = db_session.query(User).filter_by(username="commander_test").first()
    assert fetched is not None
    assert fetched.role == "Expedition Commander"
    assert fetched.full_name == "Dr. Rajesh Sharma"


def test_expedition_and_route_crud(db_session):
    """Verify Expedition and Route models."""
    exp = Expedition(
        id="EXP-2026-TEST",
        name="Maitri-II Science Traverse",
        mission="Ice sheet radar sounding and logistics depot setup",
        region="Queen Maud Land",
        start_date="2026-11-01",
        end_date="2027-02-28",
        status="ACTIVE",
        commander_name="Dr. Rajesh Sharma"
    )
    db_session.add(exp)

    route = Route(
        id="ROUTE-TEST-01",
        expedition_id="EXP-2026-TEST",
        name="Maitri to Camp Alpha",
        origin_id="MAITRI_II",
        destination_id="CAMP_ALPHA",
        distance_km=42.5,
        estimated_time_hours=2.4,
        waypoints_json=[[-70.7667, 11.7333], [-70.8000, 11.7400], [-70.8333, 11.7500]],
        danger_level="LOW",
        status="APPROVED"
    )
    db_session.add(route)
    db_session.commit()

    fetched_exp = db_session.query(Expedition).filter_by(id="EXP-2026-TEST").first()
    assert fetched_exp is not None
    fetched_route = db_session.query(Route).filter_by(id="ROUTE-TEST-01").first()
    assert fetched_route is not None
    assert len(fetched_route.waypoints_json) == 3


def test_cargo_and_inventory_crud(db_session):
    """Verify Cargo and Inventory models with thermal ranges and burn rates."""
    cargo = CargoItem(
        id="CARGO-TEST-001",
        name="Microbiome Ice Core Samples",
        category="SCIENTIFIC",
        weight_kg=120.0,
        volume_m3=0.8,
        origin_id="CAMP_ALPHA",
        destination_id="MAITRI_II",
        current_temp_c=-24.5,
        min_temp_c=-30.0,
        max_temp_c=-18.0,
        lifecycle_stage="IN_TRANSIT",
        condition="NOMINAL"
    )
    db_session.add(cargo)

    inv = InventoryRecord(
        id="INV-FUEL-M2",
        location_id="MAITRI_II",
        category="FUEL",
        name="Polar Grade Diesel",
        current_qty=8500.0,
        unit="LITERS",
        min_threshold=2500.0,
        daily_burn_rate=220.0
    )
    db_session.add(inv)
    db_session.commit()

    fetched_cargo = db_session.query(CargoItem).filter_by(id="CARGO-TEST-001").first()
    assert fetched_cargo.lifecycle_stage == "IN_TRANSIT"

    fetched_inv = db_session.query(InventoryRecord).filter_by(id="INV-FUEL-M2").first()
    assert fetched_inv.current_qty == 8500.0
    # Autonomy calculation
    autonomy_days = fetched_inv.current_qty / fetched_inv.daily_burn_rate
    assert round(autonomy_days, 1) == 38.6


def test_emergency_and_audit_crud(db_session):
    """Verify Emergency Incident and immutable Audit Log persistence."""
    incident = EmergencyIncident(
        id="INC-TEST-01",
        incident_type="CREVASSE_FALL",
        severity="CRITICAL",
        location_id="CORRIDOR_C3",
        latitude=-70.8210,
        longitude=11.7450,
        status="DISPATCHED",
        assigned_asset_id="PB-300-01"
    )
    db_session.add(incident)

    audit = AuditLog(
        operator="Dr. Rajesh Sharma",
        action="SAR_DISPATCH_AUTHORIZED",
        entity_type="SAR",
        entity_id="INC-TEST-01",
        details={"vehicle": "PB-300-01", "eta_min": 14.5}
    )
    db_session.add(audit)
    db_session.commit()

    fetched_inc = db_session.query(EmergencyIncident).filter_by(id="INC-TEST-01").first()
    assert fetched_inc.status == "DISPATCHED"

    fetched_audit = db_session.query(AuditLog).filter_by(entity_id="INC-TEST-01").first()
    assert fetched_audit.action == "SAR_DISPATCH_AUTHORIZED"


def test_database_rollback_integrity(db_session):
    """Verify transaction rollback correctly cancels uncommitted mutations."""
    try:
        invalid_cargo = CargoItem(
            id="CARGO-FAIL",
            name="Corrupted Item",
            category="TEST",
            weight_kg=50.0,
            origin_id="MAITRI_II",
            destination_id="CAMP_ALPHA"
        )
        db_session.add(invalid_cargo)
        db_session.flush()
        # Force intentional rollback
        db_session.rollback()
    except Exception:
        db_session.rollback()

    assert db_session.query(CargoItem).filter_by(id="CARGO-FAIL").first() is None


def test_db_connection_health():
    """Verify connection health checker reports structured status."""
    status = check_db_connection()
    assert "status" in status
    assert "database" in status
