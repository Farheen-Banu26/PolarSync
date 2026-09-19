import streamlit as st
import os
import sys
import pandas as pd

# Ensure parent directory is in python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from dashboard.utils.styles import POLAR_CSS
from dashboard.adapter import DashboardAdapter
from dashboard.map.polar_map import create_polar_operations_map
from dashboard.charts.telemetry_charts import (
    create_fuel_telemetry_chart,
    create_cargo_thermal_chart,
    create_speed_telemetry_chart,
    create_autonomy_trend_chart,
    create_sar_timeline_chart,
    create_connectivity_timeline_chart
)
from dashboard.components.kpi_cards import render_kpi_cards
from dashboard.components.cargo_panel import render_cargo_panel
from dashboard.components.inventory_panel import render_inventory_panel
from dashboard.components.personnel_panel import render_personnel_panel
from dashboard.components.emergency_panel import render_emergency_panel
from dashboard.components.connectivity_panel import render_connectivity_panel
from dashboard.components.alerts_panel import render_alerts_panel


# Configure Streamlit Page
st.set_page_config(
    page_title="PolarSync — Polar Expedition Command Center",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject Custom Dark Polar Styling
st.markdown(POLAR_CSS, unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def get_scenario_data(scenario_idx: int):
    adapter = DashboardAdapter(base_dir=parent_dir)
    return adapter.run_scenario(scenario_idx)


def render_event_flow(scenario_idx: int):
    """
    Render compact Operational Event Flow banner near top of dashboard using actual simulation events.
    """
    flow_definitions = {
        1: [
            ("DISPATCH", "event-node"),
            ("TRANSIT", "event-node"),
            ("CARGO DELIVERED", "event-node-success"),
            ("NOMINAL", "event-node-success")
        ],
        2: [
            ("CONSUMPTION SPIKE", "event-node-warning"),
            ("FUEL LEAK", "event-node-alert"),
            ("AUTONOMY CRITICAL", "event-node-alert"),
            ("RESUPPLY ALERT", "event-node-warning")
        ],
        3: [
            ("EMERGENCY", "event-node-alert"),
            ("MUSTER", "event-node-warning"),
            ("SAR SELECTION", "event-node"),
            ("DISPATCH", "event-node"),
            ("ON SCENE", "event-node"),
            ("RESOLVED", "event-node-success")
        ],
        4: [
            ("COOLER FAILURE", "event-node-warning"),
            ("TEMP DRIFT", "event-node-warning"),
            ("FREEZING WARNING", "event-node-alert"),
            ("COLD-CHAIN BREACH", "event-node-alert")
        ],
        5: [
            ("NETWORK LOST", "event-node-alert"),
            ("OFFLINE OPERATIONS", "event-node-warning"),
            ("30 EVENTS BUFFERED", "event-node-warning"),
            ("NETWORK RESTORED", "event-node-success"),
            ("SYNCHRONIZED", "event-node-success")
        ]
    }

    nodes = flow_definitions.get(scenario_idx, [("INITIALIZE", "event-node"), ("SIMULATE", "event-node"), ("COMPLETE", "event-node-success")])
    
    nodes_html = []
    for i, (label, css_class) in enumerate(nodes):
        nodes_html.append(f'<span class="event-node {css_class}">{label}</span>')
        if i < len(nodes) - 1:
            nodes_html.append('<span class="event-arrow">➔</span>')
            
    html_content = f"""
    <div class="event-flow-container">
        <div class="event-flow-title">
            <span>⚡ OPERATIONAL EVENT FLOW</span>
        </div>
        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
            {' '.join(nodes_html)}
        </div>
    </div>
    """
    st.markdown(html_content, unsafe_allow_html=True)


def main():
    # 1. Header Bar
    st.markdown("""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
            <div>
                <div class="header-title">❄️ PolarSync Command Center</div>
                <div class="header-subtitle">Integrated Polar Expedition Logistics and Asset Management System</div>
            </div>
            <div style="display: flex; gap: 8px; align-items: center; margin-top: 4px;">
                <span class="header-badge">SIH26062</span>
                <span class="header-badge" style="background: rgba(148, 163, 184, 0.15); color: #94a3b8; border-color: rgba(148, 163, 184, 0.3); font-size: 0.7rem;">SIMULATION MODE</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 2. Sidebar - Scenario Selector
    st.sidebar.markdown("### 🎯 Scenario Control")
    scenario_options = {
        1: "Scenario 1 — Normal Expedition Operations",
        2: "Scenario 2 — Fuel Shortage Crisis",
        3: "Scenario 3 — Personnel Emergency & SAR",
        4: "Scenario 4 — Cold-Chain Freezing Breach",
        5: "Scenario 5 — Satellite Loss & Sync"
    }

    selected_sc_idx = st.sidebar.selectbox(
        "Select Demonstration Scenario:",
        options=list(scenario_options.keys()),
        format_func=lambda x: scenario_options[x],
        index=0
    )

    run_sim_clicked = st.sidebar.button("▶ Run / Refresh Simulation", use_container_width=True, type="primary")

    # Load Scenario Simulation Data
    with st.spinner("Executing simulation kernel & processing telemetry frames..."):
        sim_data = get_scenario_data(selected_sc_idx)

    # Sidebar Scenario Information Box
    st.sidebar.markdown(f"""
    <div style="background: rgba(15, 23, 42, 0.8); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px; margin-top: 15px;">
        <div style="font-size: 0.75rem; font-weight: 700; color: #38bdf8; text-transform: uppercase;">MISSION OBJECTIVE</div>
        <div style="font-size: 0.82rem; color: #cbd5e1; margin-top: 6px; line-height: 1.4;">
            {sim_data['scenario_description']}
        </div>
        <div style="margin-top: 10px; font-size: 0.75rem; color: #94a3b8; font-family: 'JetBrains Mono';">
            Duration: {sim_data['duration_ticks']} ticks | Seed: 42
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 3. Compact Operational Event Flow Section
    render_event_flow(selected_sc_idx)

    # 4. Top KPI Cards
    render_kpi_cards(sim_data)
    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    # 5. Main Tabbed Layout
    tabs = st.tabs([
        "🗺️ Operations Map & Fleet",
        "⚡ Inventory & Autonomy",
        "📦 Cold-Chain Cargo",
        "👥 Personnel Muster",
        "🚨 Emergency & SAR Response",
        "🛰️ Satellite & Offline Sync",
        "🔔 Mission Alerts"
    ])

    # Tab 1: Operations Map & Scenario-Aware Live Telemetry Focus
    with tabs[0]:
        col_map, col_fleet = st.columns([1.5, 1])

        with col_map:
            fig_map = create_polar_operations_map(sim_data)
            st.plotly_chart(fig_map, use_container_width=True)

        with col_fleet:
            st.markdown('<div class="panel-header">🚜 Vehicle Fleet Status & Kinematics</div>', unsafe_allow_html=True)
            veh_df = sim_data["vehicles_df"]
            desired_veh_cols = ["Name", "Type", "Status", "Fuel (%)", "Speed (km/h)", "Connectivity", "Route Progress (%)"]
            avail_veh_cols = [c for c in desired_veh_cols if c in veh_df.columns]
            st.dataframe(
                veh_df[avail_veh_cols] if not veh_df.empty else pd.DataFrame(),
                use_container_width=True,
                hide_index=True,
                height=200,
                column_config={
                    "Fuel (%)": st.column_config.ProgressColumn("Fuel", min_value=0, max_value=100, format="%.0f%%"),
                    "Route Progress (%)": st.column_config.ProgressColumn("Progress", min_value=0, max_value=100, format="%.0f%%")
                }
            )

            # Scenario-Aware Primary Visualization
            if selected_sc_idx == 1:
                fig_primary = create_speed_telemetry_chart(sim_data["telemetry_df"])
            elif selected_sc_idx == 2:
                fig_primary = create_autonomy_trend_chart(sim_data["inventory_df"], sim_data["telemetry_df"])
            elif selected_sc_idx == 3:
                fig_primary = create_sar_timeline_chart(sim_data.get("active_emergency"), sim_data.get("events", []))
            elif selected_sc_idx == 4:
                fig_primary = create_cargo_thermal_chart(sim_data["cargo_history_df"], sim_data["cargo_df"])
            elif selected_sc_idx == 5:
                fig_primary = create_connectivity_timeline_chart(sim_data["telemetry_df"], sim_data.get("sync_stats", {}))
            else:
                fig_primary = create_speed_telemetry_chart(sim_data["telemetry_df"])

            st.plotly_chart(fig_primary, use_container_width=True)

    # Tab 2: Inventory & Autonomy
    with tabs[1]:
        render_inventory_panel(sim_data)
        
        # Fuel time series chart
        st.markdown("### Fleet Fuel Burn Dynamics")
        fig_fuel = create_fuel_telemetry_chart(sim_data["telemetry_df"])
        st.plotly_chart(fig_fuel, use_container_width=True)

    # Tab 3: Cold-Chain Cargo
    with tabs[2]:
        render_cargo_panel(sim_data)
        st.markdown("### Thermal Bounds & Insulation Profile")
        fig_thermal = create_cargo_thermal_chart(sim_data["cargo_history_df"], sim_data["cargo_df"])
        st.plotly_chart(fig_thermal, use_container_width=True)

    # Tab 4: Personnel Muster
    with tabs[3]:
        render_personnel_panel(sim_data)

    # Tab 5: Emergency & SAR Decision Support
    with tabs[4]:
        render_emergency_panel(sim_data)

    # Tab 6: Satellite Uplink & Offline Sync
    with tabs[5]:
        render_connectivity_panel(sim_data)

    # Tab 7: Mission Alerts
    with tabs[6]:
        render_alerts_panel(sim_data["alerts"])


if __name__ == "__main__":
    main()
