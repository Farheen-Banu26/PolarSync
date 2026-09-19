import streamlit as st
import pandas as pd
from typing import Dict, Any
from ..charts.autonomy_charts import create_autonomy_bar_chart


def render_inventory_panel(data: Dict[str, Any]):
    """
    Render inventory stocks, burn rates, and predictive autonomy risk panel.
    """
    inventory_df = data["inventory_df"]

    st.markdown('<div class="panel-header">⚡ Expedition Inventory & Days of Autonomy (DoA)</div>', unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        # Structured table with safe column subset
        desired_cols = [
            "Category", "Location Name", "Location", "Current Stock", "Daily Burn Rate",
            "Days of Autonomy", "Resupply Window (days)", "Resupply Risk"
        ]
        available_cols = [c for c in desired_cols if c in inventory_df.columns]
        display_df = inventory_df[available_cols] if not inventory_df.empty else pd.DataFrame()

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Resource"),
                "Location Name": st.column_config.TextColumn("Facility / Camp"),
                "Location": st.column_config.TextColumn("Loc ID"),
                "Current Stock": st.column_config.TextColumn("Stock Level"),
                "Daily Burn Rate": st.column_config.TextColumn("Daily Burn"),
                "Days of Autonomy": st.column_config.NumberColumn("Autonomy", format="%.1f days"),
                "Resupply Risk": st.column_config.TextColumn("Risk Tier")
            }
        )

        st.markdown("""
        <div style="font-size: 0.75rem; color: #64748b; margin-top: 6px; font-family: 'JetBrains Mono';">
            Formula: Days of Autonomy = Current Stock / Daily Consumption Rate
        </div>
        """, unsafe_allow_html=True)

    with col2:
        # Autonomy Bar Chart
        fig = create_autonomy_bar_chart(inventory_df)
        st.plotly_chart(fig, use_container_width=True)
