"""
PolarSync Database Models - SQLAlchemy ORM Definitions
SIH Problem Statement: SIH26062
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="Viewer")  # Administrator, Expedition Commander, Logistics Officer, Field Operator, Medical/Safety Officer, Viewer
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Expedition(Base):
    __tablename__ = "expeditions"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    mission = Column(Text, nullable=False)
    region = Column(String(100), nullable=False)
    start_date = Column(String(50), nullable=False)
    end_date = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="PLANNING")  # PLANNING, ACTIVE, COMPLETED, ABORTED
    commander_name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class Route(Base):
    __tablename__ = "routes"

    id = Column(String(50), primary_key=True, index=True)
    expedition_id = Column(String(50), nullable=True)
    name = Column(String(150), nullable=False)
    origin_id = Column(String(50), nullable=False)
    destination_id = Column(String(50), nullable=False)
    distance_km = Column(Float, nullable=False)
    estimated_time_hours = Column(Float, nullable=True)
    waypoints_json = Column(JSON, nullable=False)  # List of [lat, lon] coordinates
    danger_level = Column(String(50), default="LOW")
    status = Column(String(50), default="PLANNED")  # PLANNED, APPROVED, IN_PROGRESS, COMPLETED


class CargoItem(Base):
    __tablename__ = "cargo_items"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(100), nullable=False)
    weight_kg = Column(Float, nullable=False)
    volume_m3 = Column(Float, nullable=True)
    origin_id = Column(String(50), nullable=False)
    destination_id = Column(String(50), nullable=False)
    assigned_vehicle_id = Column(String(50), nullable=True)
    current_temp_c = Column(Float, nullable=True)
    min_temp_c = Column(Float, nullable=True)
    max_temp_c = Column(Float, nullable=True)
    lifecycle_stage = Column(String(50), default="CREATED")  # CREATED, PACKED, ASSIGNED, IN_TRANSIT, DELIVERED
    condition = Column(String(50), default="NOMINAL")  # NOMINAL, BREACHED_DAMAGED, DELAYED


class InventoryRecord(Base):
    __tablename__ = "inventory_records"

    id = Column(String(50), primary_key=True, index=True)
    location_id = Column(String(50), nullable=False)
    category = Column(String(100), nullable=False)  # FUEL, FOOD, WATER, MEDICAL, SPARES, BATTERIES
    name = Column(String(150), nullable=False)
    current_qty = Column(Float, nullable=False)
    unit = Column(String(50), nullable=False)
    min_threshold = Column(Float, nullable=False)
    daily_burn_rate = Column(Float, nullable=False)


class PersonnelMember(Base):
    __tablename__ = "personnel_members"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(String(100), nullable=False)
    team = Column(String(100), nullable=False)
    location_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    shift = Column(String(50), default="DAY_SHIFT")
    comms_status = Column(String(50), default="ONLINE")
    muster_status = Column(String(50), default="CHECKED_IN")


class AssetVehicle(Base):
    __tablename__ = "asset_vehicles"

    id = Column(String(50), primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(100), nullable=False)
    location_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    heading_deg = Column(Float, default=0.0)
    speed_kmh = Column(Float, default=0.0)
    fuel_pct = Column(Float, default=100.0)
    battery_pct = Column(Float, default=100.0)
    status = Column(String(50), default="AVAILABLE")
    capabilities_json = Column(JSON, nullable=True)


class EmergencyIncident(Base):
    __tablename__ = "emergency_incidents"

    id = Column(String(50), primary_key=True, index=True)
    incident_type = Column(String(100), nullable=False)
    severity = Column(String(50), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW
    location_id = Column(String(50), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(50), default="ACTIVE")  # DETECTED, MUSTER, DISPATCHED, ON_SCENE, RESOLVED
    assigned_asset_id = Column(String(50), nullable=True)
    reported_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AlertRecord(Base):
    __tablename__ = "alert_records"

    id = Column(String(50), primary_key=True, index=True)
    severity = Column(String(50), nullable=False)  # CRITICAL, WARNING, INFO
    type = Column(String(100), nullable=False)
    source = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="NEW")  # NEW, ACKNOWLEDGED, IN_PROGRESS, RESOLVED
    related_entity_type = Column(String(50), nullable=True)
    related_entity_id = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    operator = Column(String(100), nullable=False, default="SYSTEM")
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=False)
    entity_id = Column(String(100), nullable=False)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
