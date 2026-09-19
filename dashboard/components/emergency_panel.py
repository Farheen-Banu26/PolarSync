import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_emergency_panel(data: Dict[str, Any]):
    """
    Render Emergency Decision Support Panel, SAR Asset Evaluation & Response Lifecycle.
    """
    emergency = data.get("active_emergency")
    sar_result = data.get("sar_result")

    st.markdown('<div class="panel-header">🚨 Search and Rescue (SAR) Decision Support & Incident Response</div>', unsafe_allow_html=True)

    if not emergency:
        st.info("No active emergency detected in this scenario. Fleet is on standard operational readiness.")
        return

    # Response Lifecycle Progress Bar
    current_status = emergency.status.value
    steps = ["DETECTED", "MUSTER", "DISPATCHED", "ON SCENE", "RESOLVED"]
    
    # Map current emergency status enum value to step index
    status_map = {
        "REPORTED": 0,
        "DETECTED": 0,
        "MUSTER_COMPLETED": 1,
        "MUSTER": 1,
        "ASSET_EVALUATED": 1,
        "DISPATCHED": 2,
        "ON_SCENE": 3,
        "RESOLVED": 4
    }
    status_idx = status_map.get(current_status, len(steps) - 1)

    st.markdown("### Incident Lifecycle Pipeline")
    step_cols = st.columns(5)
    step_data = [
        ("1. DETECTED", "Crevasse fall at C-3"),
        ("2. MUSTER", "Personnel roll-call"),
        ("3. DISPATCHED", "HELI-01 SAR enroute"),
        ("4. ON SCENE", "Medic arrived at C-3"),
        ("5. RESOLVED", "Casualty extracted")
    ]

    for i, (s_title, s_desc) in enumerate(step_data):
        with step_cols[i]:
            if i <= status_idx:
                card_bg = "rgba(2, 132, 199, 0.2)"
                card_border = "#38bdf8"
                title_color = "#38bdf8"
                shadow = "0 0 10px rgba(56, 189, 248, 0.3)"
            else:
                card_bg = "rgba(15, 23, 42, 0.6)"
                card_border = "rgba(148, 163, 184, 0.2)"
                title_color = "#64748b"
                shadow = "none"

            st.markdown(f"""
            <div style="background: {card_bg}; border: 1.5px solid {card_border}; border-radius: 8px; padding: 10px 8px; text-align: center; box-shadow: {shadow}; min-height: 68px;">
                <div style="font-weight: 800; font-size: 0.8rem; color: {title_color}; font-family: 'JetBrains Mono';">{s_title}</div>
                <div style="font-size: 0.7rem; color: #94a3b8; margin-top: 3px;">{s_desc}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-bottom: 14px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1.2])

    with col1:
        st.markdown(f"""
        <div style="background: rgba(239, 68, 68, 0.08); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 10px; padding: 16px;">
            <div style="font-size: 0.8rem; font-weight: 700; color: #f87171; text-transform: uppercase;">INCIDENT METADATA</div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #f8fafc; margin-top: 4px;">{emergency.incident_type}</div>
            <div style="margin-top: 8px; font-size: 0.85rem; color: #cbd5e1; line-height: 1.6;">
                <b>Incident ID:</b> <span style="font-family: 'JetBrains Mono'; color: #38bdf8;">{emergency.id}</span><br>
                <b>Location:</b> {emergency.nearest_landmark} ({emergency.location[0]:.4f}, {emergency.location[1]:.4f})<br>
                <b>Severity:</b> <span style="color: #ef4444; font-weight: 700;">{emergency.severity.value}</span><br>
                <b>Affected Personnel:</b> {', '.join(emergency.affected_personnel_ids)} ({emergency.affected_count} members)<br>
                <b>Required Capabilities:</b> {', '.join([c.value for c in emergency.required_capabilities])}<br>
                <b>Incident Status:</b> <span style="color: #4ade80; font-weight: 700;">{emergency.status.value}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        if sar_result and sar_result.selected_vehicle_id:
            winning_eval = next((e for e in sar_result.evaluations if e.vehicle_id == sar_result.selected_vehicle_id), None)
            
            explanation_html = ""
            if winning_eval:
                for pt in winning_eval.explanation_points:
                    explanation_html += f"<div style='margin-top: 4px;'>✅ <span style='color: #e2e8f0;'>{pt}</span></div>"

            st.markdown(f"""
            <div style="background: rgba(15, 23, 42, 0.9); border: 1px solid rgba(56, 189, 248, 0.3); border-radius: 10px; padding: 16px;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">RECOMMENDED RESPONSE ASSET (DECISION SUPPORT)</div>
                <div style="font-size: 1.3rem; font-weight: 700; color: #38bdf8; margin-top: 4px;">
                    {sar_result.selected_vehicle_name} <span style="font-size: 0.9rem; color: #94a3b8;">({sar_result.selected_vehicle_id})</span>
                </div>
                <div style="font-size: 0.82rem; color: #4ade80; font-weight: 600; margin-top: 2px;">
                    Composite Suitability Score: {winning_eval.score:.1f} / 100 | ETA: {winning_eval.estimated_transit_time_min:.0f} mins
                </div>
                <div style="margin-top: 10px; font-size: 0.82rem; color: #cbd5e1; line-height: 1.5;">
                    {explanation_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Fleet Comparison Table
    if sar_result:
        st.markdown("### Fleet Evaluation & Suitability Matrix")
        eval_rows = []
        for ev in sar_result.evaluations:
            eval_rows.append({
                "Asset": ev.vehicle_name,
                "Type": ev.vehicle_type,
                "Distance": f"{ev.distance_km:.1f} km",
                "Est. ETA": f"{ev.estimated_transit_time_min:.0f} mins",
                "Fuel Remaining": f"{ev.fuel_remaining_pct:.0f}%",
                "Post-Mission Fuel": f"{ev.fuel_after_mission_pct:.0f}%",
                "Eligibility": "QUALIFIED" if ev.is_eligible else "DISQUALIFIED",
                "Score": f"{ev.score:.1f} / 100" if ev.is_eligible else "-",
                "Disqualification / Rationale": ", ".join(ev.disqualification_reasons) if not ev.is_eligible else "Meets range & capabilities"
            })
        
        st.dataframe(
            pd.DataFrame(eval_rows),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Asset": st.column_config.TextColumn("Vehicle Name", width="medium"),
                "Type": st.column_config.TextColumn("Type", width="small"),
                "Distance": st.column_config.TextColumn("Distance", width="small"),
                "Est. ETA": st.column_config.TextColumn("ETA", width="small"),
                "Fuel Remaining": st.column_config.TextColumn("Fuel", width="small"),
                "Post-Mission Fuel": st.column_config.TextColumn("Post-Fuel", width="small"),
                "Eligibility": st.column_config.TextColumn("Status", width="small"),
                "Score": st.column_config.TextColumn("Score", width="small"),
                "Disqualification / Rationale": st.column_config.TextColumn("Evaluation Rationale", width="large")
            }
        )
