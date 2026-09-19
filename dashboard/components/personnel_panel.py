import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_personnel_panel(data: Dict[str, Any]):
    """
    Render personnel roster, muster roll-call summary, and movement statuses.
    """
    pers_df = data["personnel_df"]
    muster = data.get("muster_report")

    st.markdown('<div class="panel-header">👥 Personnel Roster & Roll-Call Muster</div>', unsafe_allow_html=True)

    if muster:
        # Muster Summary Badges
        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 14px; flex-wrap: wrap;">
            <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.3); padding: 8px 14px; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #94a3b8;">TOTAL EXPECTED:</span> 
                <b style="color: #f8fafc; font-family: 'JetBrains Mono'; font-size: 1.1rem; margin-left: 6px;">{muster.total_expected}</b>
            </div>
            <div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); padding: 8px 14px; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #4ade80;">BASE / CHECKED-IN:</span> 
                <b style="color: #4ade80; font-family: 'JetBrains Mono'; font-size: 1.1rem; margin-left: 6px;">{muster.checked_in_count}</b>
            </div>
            <div style="background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.3); padding: 8px 14px; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #38bdf8;">FIELD TEAMS:</span> 
                <b style="color: #38bdf8; font-family: 'JetBrains Mono'; font-size: 1.1rem; margin-left: 6px;">{muster.field_count}</b>
            </div>
            <div style="background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.4); padding: 8px 14px; border-radius: 8px;">
                <span style="font-size: 0.75rem; color: #f87171;">UNCONFIRMED / MISSING:</span> 
                <b style="color: #f87171; font-family: 'JetBrains Mono'; font-size: 1.1rem; margin-left: 6px;">{muster.unconfirmed_count}</b>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Personnel Table with safe column filtering
    desired_cols = ["ID", "Name", "Role", "Location / Assigned Base", "Current Position", "Movement Status", "Status", "Heartbeat"]
    available_cols = [c for c in desired_cols if c in pers_df.columns]
    display_df = pers_df[available_cols] if not pers_df.empty else pd.DataFrame()
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        height=260,
        column_config={
            "ID": st.column_config.TextColumn("ID", width="small"),
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Role": st.column_config.TextColumn("Duty Role"),
            "Movement Status": st.column_config.TextColumn("Movement"),
            "Status": st.column_config.TextColumn("Muster Status"),
            "Heartbeat": st.column_config.TextColumn("Link")
        }
    )
