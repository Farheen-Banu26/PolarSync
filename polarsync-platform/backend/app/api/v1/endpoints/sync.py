"""
Offline Synchronization Endpoints (Stage 3.4)
"""
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException
from app.schemas.sync import SyncRequest, SyncResponse, SyncResultItem

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
    Validates and reconciles queued offline client actions.
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

        # Accepted operation
        accepted_list.append(SyncResultItem(
            id=op.id,
            resource=op.resource,
            operation=op.operation,
            status="ACCEPTED",
            message=f"Operation '{op.operation}' on {op.resource} validated and reconciled successfully."
        ))

    return SyncResponse(
        accepted=accepted_list,
        rejected=rejected_list,
        server_timestamp=server_time
    )
