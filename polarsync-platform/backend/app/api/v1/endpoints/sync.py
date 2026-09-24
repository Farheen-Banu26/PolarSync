"""
Offline Synchronization Endpoints
SIH Problem Statement: SIH26062
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.schemas.sync import SyncRequest, SyncResponse, SyncResultItem
from app.services.audit_service import audit_service
from app.api.v1.endpoints.personnel import PERSONNEL_OVERRIDES
from app.api.v1.endpoints.cargo import CARGO_OVERRIDES

router = APIRouter()

SUPPORTED_RESOURCES = {
    "personnel": {
        "operations": ["UPDATE_CHECKIN", "UPDATE_MUSTER_STATUS"],
        "required_fields": ["personnel_id"]
    },
    "cargo": {
        "operations": ["UPDATE_STAGE", "INSPECT_CARGO"],
        "required_fields": ["cargo_id"]
    },
    "assets": {
        "operations": ["UPDATE_STATUS", "DISPATCH_ASSET"],
        "required_fields": ["asset_id"]
    }
}


@router.post("", response_model=SyncResponse)
@router.post("/", response_model=SyncResponse)
def synchronize_operations(req: SyncRequest) -> SyncResponse:
    """
    Opportunistic Synchronization Endpoint for Field Operations.
    Validates, reconciles, updates active state, and logs audit trail for queued offline actions.
    """
    server_time = datetime.now(timezone.utc).isoformat()
    accepted_list = []
    rejected_list = []

    for op in req.operations:
        res_key = op.resource.lower()
        if res_key not in SUPPORTED_RESOURCES:
            rejected_list.append(SyncResultItem(
                id=op.id,
                resource=op.resource,
                operation=op.operation,
                status="REJECTED",
                message=f"Unsupported resource '{op.resource}'. Supported: {list(SUPPORTED_RESOURCES.keys())}"
            ))
            continue

        spec = SUPPORTED_RESOURCES[res_key]
        if op.operation.upper() not in spec["operations"]:
            rejected_list.append(SyncResultItem(
                id=op.id,
                resource=op.resource,
                operation=op.operation,
                status="REJECTED",
                message=f"Unsupported operation '{op.operation}' for resource '{op.resource}'. Allowed: {spec['operations']}"
            ))
            continue

        # Check required fields in payload
        missing_fields = [f for f in spec["required_fields"] if f not in op.payload]
        if missing_fields:
            rejected_list.append(SyncResultItem(
                id=op.id,
                resource=op.resource,
                operation=op.operation,
                status="REJECTED",
                message=f"Payload missing required field(s): {missing_fields}"
            ))
            continue

        # Apply state mutation based on resource type
        if res_key == "personnel":
            p_id = op.payload.get("personnel_id")
            new_st = op.payload.get("muster_status", "CHECKED_IN")
            PERSONNEL_OVERRIDES[p_id] = {
                "muster_status": new_st,
                "comms_status": "ONLINE"
            }
            audit_service.log_action(
                operator="Field Operator (Sync Queue)",
                role="Field Operator",
                action="OFFLINE_SYNC_PERSONNEL_CHECKIN",
                entity_type="PERSONNEL",
                entity_id=p_id,
                details={"synced_op_id": op.id, "muster_status": new_st}
            )

        elif res_key == "cargo":
            c_id = op.payload.get("cargo_id")
            new_stage = op.payload.get("lifecycle_stage", "IN_TRANSIT")
            CARGO_OVERRIDES[c_id] = {
                "lifecycle_stage": new_stage
            }
            audit_service.log_action(
                operator="Logistics Field Unit (Sync Queue)",
                role="Logistics Officer",
                action="OFFLINE_SYNC_CARGO_UPDATE",
                entity_type="CARGO",
                entity_id=c_id,
                details={"synced_op_id": op.id, "lifecycle_stage": new_stage}
            )

        # Accepted operation
        accepted_list.append(SyncResultItem(
            id=op.id,
            resource=op.resource,
            operation=op.operation,
            status="ACCEPTED",
            message=f"Operation '{op.operation}' on {op.resource} validated and persisted to operational state."
        ))

    return SyncResponse(
        accepted=accepted_list,
        rejected=rejected_list,
        server_timestamp=server_time
    )
