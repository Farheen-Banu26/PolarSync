import streamlit as st
from typing import Dict, Any


def render_kpi_cards(data: Dict[str, Any]):
    """
    Render 6 high-level glassmorphic KPI status cards.
    """
    readiness = data["readiness_report"]
    net_status = data["network_status"]
    pers_df = data["personnel_df"]
    veh_df = data["vehicles_df"]
    cargo_df = data["cargo_df"]
    alerts = data["alerts"]

    # Calculate metrics
    readiness_status = readiness.overall_status
    status_badge_class = {
        "NOMINAL": "badge-nominal",
        "CONDITIONAL": "badge-conditional",
        "DEGRADED": "badge-degraded",
        "CRITICAL": "badge-critical"
    }.get(readiness_status, "badge-nominal")

    total_pers = len(pers_df)
    active_pers = len(pers_df[pers_df["Status"].isin(["ACTIVE_NORMAL", "CHECKED_IN", "EVACUATED"])])
    muster = data.get("muster_report")
    emergency = data.get("active_emergency")

    if muster and muster.unconfirmed_count > 0 and (emergency and emergency.status.value != "RESOLVED"):
        muster_display = f"{muster.checked_in_count}/{muster.total_expected}"
        muster_sub = f"<span style='color: #f87171; font-weight: 700;'>{muster.unconfirmed_count} UNCONFIRMED</span>"
    else:
        muster_display = f"{total_pers}/{total_pers}"
        muster_sub = "<span style='color: #4ade80; font-weight: 600;'>ALL ACCOUNTED</span>"

    total_veh = len(veh_df)
    avail_veh = len(veh_df[veh_df["Status"] == "AVAILABLE"])

    total_cargo = len(cargo_df)
    nominal_cargo = len(cargo_df[cargo_df["Condition"] != "BREACHED_DAMAGED"])
    cargo_pct = int((nominal_cargo / total_cargo) * 100) if total_cargo > 0 else 100

    crit_alerts = sum(1 for a in alerts if a.severity.value == "CRITICAL")
    warn_alerts = sum(1 for a in alerts if a.severity.value == "WARNING")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Expedition Readiness</div>
            <div class="kpi-value"><span class="{status_badge_class}">{readiness_status}</span></div>
            <div class="kpi-sub">Composite Autonomy Index</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        net_color = "#22c55e" if net_status == "ONLINE" else "#ef4444"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Satellite Uplink</div>
            <div class="kpi-value" style="color: {net_color};">{net_status}</div>
            <div class="kpi-sub">{"Store-and-Forward Active" if net_status == "OFFLINE" else "Direct Telemetry Stream"}</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Personnel Muster</div>
            <div class="kpi-value">{muster_display}</div>
            <div class="kpi-sub">{muster_sub}</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Active Fleet</div>
            <div class="kpi-value">{avail_veh}/{total_veh}</div>
            <div class="kpi-sub">Vehicles Operational</div>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        cargo_color = "#22c55e" if cargo_pct >= 90 else ("#facc15" if cargo_pct >= 60 else "#ef4444")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Cold-Chain Health</div>
            <div class="kpi-value" style="color: {cargo_color};">{cargo_pct}%</div>
            <div class="kpi-sub">Thermal Bounds Intact</div>
        </div>
        """, unsafe_allow_html=True)

    with col6:
        alert_color = "#ef4444" if crit_alerts > 0 else ("#f59e0b" if warn_alerts > 0 else "#38bdf8")
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Alert Engine</div>
            <div class="kpi-value" style="color: {alert_color};">{len(alerts)}</div>
            <div class="kpi-sub">{crit_alerts} Critical | {warn_alerts} Warning</div>
        </div>
        """, unsafe_allow_html=True)
