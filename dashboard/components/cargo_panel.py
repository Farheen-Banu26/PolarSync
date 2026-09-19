import streamlit as st
import pandas as pd
from typing import Dict, Any


def render_cargo_panel(data: Dict[str, Any]):
    """
    Render cold-chain cargo tracking panel with 7-stage lifecycle pipeline.
    """
    cargo_df = data["cargo_df"]

    st.markdown('<div class="panel-header">📦 Cold-Chain Cargo Tracking & Lifecycle Management</div>', unsafe_allow_html=True)

    # Lifecycle Stepper Reference
    st.markdown("""
    <div style="background: rgba(15, 23, 42, 0.6); padding: 12px 16px; border-radius: 8px; border: 1px solid rgba(56, 189, 248, 0.2); margin-bottom: 15px;">
        <span style="font-size: 0.8rem; font-weight: 700; color: #38bdf8;">LIFECYCLE PIPELINE:</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #94a3b8; margin-left: 8px;">
            PACKED <span style="color: #38bdf8;">➔</span> 
            QC <span style="color: #38bdf8;">➔</span> 
            LOADED <span style="color: #38bdf8;">➔</span> 
            IN_TRANSIT <span style="color: #38bdf8;">➔</span> 
            ARRIVED <span style="color: #38bdf8;">➔</span> 
            INSPECTED <span style="color: #38bdf8;">➔</span> 
            <b style="color: #4ade80;">DELIVERED</b>
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Format cargo table with styled condition badges
    display_df = cargo_df.copy()
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Cargo ID": st.column_config.TextColumn("Cargo ID", width="small"),
            "Name": st.column_config.TextColumn("Item Name", width="medium"),
            "Category": st.column_config.TextColumn("Category", width="small"),
            "Lifecycle Stage": st.column_config.TextColumn("Stage", width="small"),
            "Temperature (°C)": st.column_config.NumberColumn("Temp (°C)", format="%.1f °C"),
            "Allowed Range": st.column_config.TextColumn("Safe Bounds"),
            "Condition": st.column_config.TextColumn("Thermal Status"),
            "Cooling Active": st.column_config.TextColumn("Refrigeration")
        }
    )
