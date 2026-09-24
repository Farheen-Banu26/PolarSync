"""
PolarSync Authentication & Role-Based Access Control (RBAC)
SIH Problem Statement: SIH26062
"""
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Callable
import hashlib
from fastapi import APIRouter, HTTPException, Depends, Header, status
from pydantic import BaseModel, EmailStr
from app.core.config import settings
from app.services.audit_service import audit_service

router = APIRouter()

# Pre-configured demo expedition personnel profiles for SIH evaluation
DEMO_USERS = {
    "commander": {
        "username": "commander",
        "full_name": "Dr. Rajesh Sharma",
        "role": "Expedition Commander",
        "email": "rajesh.sharma@ncpor.gov.in",
        "station": "Maitri-II Main Station",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["PLAN_EXPEDITION", "DISPATCH_SAR", "RESOLVE_EMERGENCY", "APPROVE_ROUTES", "OVERRIDE_SAFETY", "MANAGE_FLEET", "ACKNOWLEDGE_ALERTS", "UPDATE_CARGO", "MUSTER_CHECKIN"]
    },
    "logistics": {
        "username": "logistics",
        "full_name": "Lt. Col. Vikram Rao",
        "role": "Logistics Officer",
        "email": "vikram.rao@ncpor.gov.in",
        "station": "Maitri-II Main Station",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["MANAGE_CARGO", "UPDATE_INVENTORY", "ASSIGN_VEHICLES", "CREATE_RESUPPLY_ORDER", "ACKNOWLEDGE_ALERTS", "UPDATE_CARGO"]
    },
    "safety": {
        "username": "safety",
        "full_name": "Dr. Ananya Sen (MD)",
        "role": "Medical/Safety Officer",
        "email": "ananya.sen@ncpor.gov.in",
        "station": "Maitri-II Main Station",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["TRIAGE_EMERGENCY", "DECLARE_MUSTER", "DISPATCH_SAR", "ACKNOWLEDGE_ALERTS", "RESOLVE_EMERGENCY", "MUSTER_CHECKIN"]
    },
    "operator": {
        "username": "operator",
        "full_name": "Suresh Patel",
        "role": "Field Operator",
        "email": "suresh.patel@ncpor.gov.in",
        "station": "Camp Alpha (Schirmacher)",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["CHECK_IN", "MUSTER_CHECKIN", "UPDATE_CARGO_STAGE", "UPDATE_CARGO", "SUBMIT_TELEMETRY", "SYNC_OFFLINE", "ACKNOWLEDGE_ALERTS"]
    },
    "admin": {
        "username": "admin",
        "full_name": "Polar Operations Central Admin",
        "role": "Administrator",
        "email": "admin@polarsync.ncpor.gov.in",
        "station": "NCPOR HQ (Goa)",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["*"]
    },
    "viewer": {
        "username": "viewer",
        "full_name": "Public Science Observer",
        "role": "Viewer",
        "email": "observer@moes.gov.in",
        "station": "Remote Observer",
        "password_hash": hashlib.sha256("polar2026".encode()).hexdigest(),
        "permissions": ["READ_ONLY"]
    }
}


class LoginRequest(BaseModel):
    username: str
    password: str


class UserProfile(BaseModel):
    username: str
    full_name: str
    role: str
    email: str
    station: str
    permissions: List[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


def resolve_user_from_token(authorization: Optional[str] = Header(None)) -> UserProfile:
    """
    Resolves active user from Bearer header or returns default Commander.
    """
    if not authorization:
        u = DEMO_USERS["commander"]
        return UserProfile(**{k: v for k, v in u.items() if k != "password_hash"})

    token = authorization.replace("Bearer ", "").strip()
    for uname, u in DEMO_USERS.items():
        if uname in token.lower():
            return UserProfile(**{k: v for k, v in u.items() if k != "password_hash"})

    # If unknown token format, raise 401
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication token.")


def require_permission(required_perm: str) -> Callable:
    """
    FastAPI dependency generator enforcing RBAC permissions on mutating operations.
    """
    def _dependency(user: UserProfile = Depends(resolve_user_from_token)) -> UserProfile:
        if "*" in user.permissions:
            return user
        if user.role == "Viewer" or required_perm not in user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access Denied: Role '{user.role}' lacks '{required_perm}' permission required for this operation."
            )
        return user
    return _dependency


@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    uname = req.username.lower().strip()
    user = DEMO_USERS.get(uname)

    # Simple secure check for demo passwords (default: polar2026)
    input_hash = hashlib.sha256(req.password.encode()).hexdigest()
    if not user or (req.password != "polar2026" and input_hash != user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password. Default demo password is 'polar2026'.")

    token = f"polarsync_{uname}_{int(datetime.now(timezone.utc).timestamp())}"
    
    audit_service.log_action(
        operator=user["full_name"],
        role=user["role"],
        action="USER_LOGIN",
        entity_type="AUTH",
        entity_id=uname,
        details={"station": user["station"], "login_time": datetime.now(timezone.utc).isoformat()}
    )

    return LoginResponse(
        access_token=token,
        user=UserProfile(
            username=user["username"],
            full_name=user["full_name"],
            role=user["role"],
            email=user["email"],
            station=user["station"],
            permissions=user["permissions"]
        )
    )


@router.get("/me", response_model=UserProfile)
def get_current_user(user: UserProfile = Depends(resolve_user_from_token)):
    return user


@router.get("/roles", response_model=List[UserProfile])
def list_available_roles():
    """
    List all pre-configured operational roles for SIH presentation switching.
    """
    return [
        UserProfile(
            username=u["username"],
            full_name=u["full_name"],
            role=u["role"],
            email=u["email"],
            station=u["station"],
            permissions=u["permissions"]
        )
        for u in DEMO_USERS.values()
    ]
