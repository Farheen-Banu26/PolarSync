import plotly.graph_objects as go
import pandas as pd
from typing import Dict, Any


def create_fuel_telemetry_chart(telemetry_df: pd.DataFrame) -> go.Figure:
    """
    Time-series fuel percentage chart for all active vehicles.
    """
    fig = go.Figure()
    if telemetry_df is None or telemetry_df.empty or "vehicle_id" not in telemetry_df.columns:
        fig.update_layout(
            title=dict(text="<b>FLEET FUEL CONSUMPTION (No Telemetry Available)</b>", font=dict(size=13, color="#38bdf8")),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#e2e8f0"),
            height=320
        )
        return fig

    vehicles = telemetry_df["vehicle_id"].unique()
    colors = ["#38bdf8", "#34d399", "#facc15", "#f43f5e", "#a78bfa", "#fb923c"]

    for i, v_id in enumerate(vehicles):
        v_data = telemetry_df[telemetry_df["vehicle_id"] == v_id]
        if "tick" in v_data.columns and "fuel_pct" in v_data.columns:
            fig.add_trace(go.Scatter(
                x=v_data["tick"],
                y=v_data["fuel_pct"],
                mode="lines",
                name=str(v_id),
                line=dict(width=2, color=colors[i % len(colors)])
            ))

    # Add 25% safety reserve threshold line
    fig.add_hline(
        y=25.0,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Critical Reserve (25%)",
        annotation_position="bottom right",
        annotation_font_color="#f87171"
    )

    fig.update_layout(
        title=dict(text="<b>FLEET FUEL CONSUMPTION & RESERVES (% Capacity)</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Simulation Tick (Minutes)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Fuel Level (%)", range=[0, 105], gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=10, color="#94a3b8")),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320
    )
    return fig


def create_cargo_thermal_chart(cargo_history_df: pd.DataFrame, cargo_df: pd.DataFrame) -> go.Figure:
    """
    Cold-chain temperature tracking chart comparing actual cargo temperature
    against allowed minimum and maximum safe thresholds.
    """
    fig = go.Figure()

    if cargo_history_df is None or cargo_history_df.empty or cargo_df is None or cargo_df.empty:
        fig.update_layout(
            title=dict(text="<b>COLD-CHAIN THERMAL INTEGRITY (No Data Available)</b>", font=dict(size=13, color="#38bdf8")),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#e2e8f0"),
            height=320
        )
        return fig

    # Focus on temperature-sensitive cargo
    sens_cargo = cargo_df[cargo_df["Category"] == "MEDICAL_SAMPLES"] if "Category" in cargo_df.columns else pd.DataFrame()
    if sens_cargo.empty and "Cargo ID" in cargo_df.columns:
        c_id = cargo_df["Cargo ID"].iloc[0]
        min_temp = cargo_df["Min Temp (°C)"].iloc[0] if "Min Temp (°C)" in cargo_df.columns else -25.0
        max_temp = cargo_df["Max Temp (°C)"].iloc[0] if "Max Temp (°C)" in cargo_df.columns else -15.0
    elif not sens_cargo.empty:
        c_id = sens_cargo["Cargo ID"].iloc[0]
        min_temp = sens_cargo["Min Temp (°C)"].iloc[0] if "Min Temp (°C)" in sens_cargo.columns else -25.0
        max_temp = sens_cargo["Max Temp (°C)"].iloc[0] if "Max Temp (°C)" in sens_cargo.columns else -15.0
    else:
        c_id = "CARGO"
        min_temp = -25.0
        max_temp = -15.0

    if "cargo_id" in cargo_history_df.columns:
        c_hist = cargo_history_df[cargo_history_df["cargo_id"] == c_id]
    else:
        c_hist = cargo_history_df

    if not c_hist.empty and "tick" in c_hist.columns and "temperature_c" in c_hist.columns:
        fig.add_trace(go.Scatter(
            x=c_hist["tick"],
            y=c_hist["temperature_c"],
            mode="lines+markers",
            name=f"{c_id} Core Temp",
            line=dict(color="#38bdf8", width=3),
            marker=dict(size=4)
        ))

    # Safe range upper and lower bounds
    fig.add_hline(y=max_temp, line_dash="dash", line_color="#ef4444", annotation_text=f"Max Allowed Limit ({max_temp}°C)", annotation_font_color="#f87171")
    fig.add_hline(y=min_temp, line_dash="dash", line_color="#38bdf8", annotation_text=f"Min Freeze Limit ({min_temp}°C)", annotation_font_color="#38bdf8")

    # Safe temperature envelope band
    fig.add_hrect(
        y0=min_temp,
        y1=max_temp,
        fillcolor="rgba(34, 197, 94, 0.08)",
        line_width=0,
        annotation_text="NOMINAL SAFE THERMAL BAND",
        annotation_position="top left",
        annotation_font_color="#4ade80"
    )

    fig.update_layout(
        title=dict(text=f"<b>COLD-CHAIN THERMAL INTEGRITY ({c_id})</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Simulation Tick (Minutes)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Temperature (°C)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=10, color="#94a3b8")),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320
    )
    return fig


def create_speed_telemetry_chart(telemetry_df: pd.DataFrame) -> go.Figure:
    """
    Speed and transit telemetry chart for active assets.
    """
    fig = go.Figure()
    if telemetry_df is None or telemetry_df.empty or "vehicle_id" not in telemetry_df.columns:
        fig.update_layout(
            title=dict(text="<b>FLEET VELOCITY PROFILE (No Telemetry Available)</b>", font=dict(size=13, color="#38bdf8")),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#e2e8f0"),
            height=320
        )
        return fig

    vehicles = telemetry_df["vehicle_id"].unique()
    colors = ["#38bdf8", "#34d399", "#facc15", "#f43f5e", "#a78bfa", "#fb923c"]

    for i, v_id in enumerate(vehicles):
        v_data = telemetry_df[telemetry_df["vehicle_id"] == v_id]
        if "tick" in v_data.columns and "speed_kmh" in v_data.columns:
            fig.add_trace(go.Scatter(
                x=v_data["tick"],
                y=v_data["speed_kmh"],
                mode="lines",
                name=str(v_id),
                line=dict(width=1.8, color=colors[i % len(colors)])
            ))

    fig.update_layout(
        title=dict(text="<b>FLEET VELOCITY PROFILE (km/h)</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Simulation Tick (Minutes)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Speed (km/h)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=10, color="#94a3b8")),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320
    )
    return fig


def create_autonomy_trend_chart(inventory_df: pd.DataFrame, telemetry_df: pd.DataFrame = None) -> go.Figure:
    """
    Scenario 2 Primary Chart: Days of Autonomy & Critical Resupply Risk across Base and Field Camps.
    Uses actual inventory dataframe columns: Category, Location, Days of Autonomy, Resupply Risk, Resupply Window.
    """
    fig = go.Figure()

    if inventory_df is None or inventory_df.empty:
        fig.update_layout(
            title=dict(text="<b>FUEL AUTONOMY DAYS (No Inventory Data Available)</b>", font=dict(size=13, color="#38bdf8")),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#e2e8f0"),
            height=320
        )
        return fig

    # Filter for fuel inventory if available; otherwise use all inventory items
    if "Category" in inventory_df.columns and "FUEL" in inventory_df["Category"].values:
        plot_df = inventory_df[inventory_df["Category"] == "FUEL"].copy()
    else:
        plot_df = inventory_df.copy()

    # Determine display label (prefer Location Name, fallback to Location or Category)
    if "Location Name" in plot_df.columns:
        labels = plot_df["Location Name"].tolist()
    elif "Location" in plot_df.columns:
        labels = plot_df["Location"].tolist()
    elif "Category" in plot_df.columns:
        labels = plot_df["Category"].tolist()
    else:
        labels = [f"Item {i+1}" for i in range(len(plot_df))]

    # Determine Autonomy value
    if "Days of Autonomy" in plot_df.columns:
        autonomies = [float(val) for val in plot_df["Days of Autonomy"].tolist()]
    elif "Stock Numeric" in plot_df.columns:
        autonomies = [float(val) for val in plot_df["Stock Numeric"].tolist()]
    else:
        autonomies = [0.0] * len(plot_df)

    # Determine risk colors
    risks = plot_df["Resupply Risk"].tolist() if "Resupply Risk" in plot_df.columns else []
    risk_colors = {
        "LOW_SAFE": "#22c55e",
        "MODERATE": "#eab308",
        "HIGH": "#f97316",
        "CRITICAL": "#ef4444"
    }

    colors = []
    for idx, doa in enumerate(autonomies):
        r = risks[idx] if idx < len(risks) else None
        if r and r in risk_colors:
            colors.append(risk_colors[r])
        elif doa < 7.0:
            colors.append("#ef4444")
        elif doa < 14.0:
            colors.append("#f97316")
        elif doa < 20.0:
            colors.append("#eab308")
        else:
            colors.append("#22c55e")

    fig.add_trace(go.Bar(
        x=labels,
        y=autonomies,
        marker=dict(color=colors, line=dict(color="rgba(255, 255, 255, 0.2)", width=1)),
        name="Fuel Autonomy (Days)",
        text=[f"{a:.1f}d" for a in autonomies],
        textposition="auto",
        textfont=dict(color="#ffffff", family="JetBrains Mono", size=11)
    ))

    # Add 7-Day Critical Threshold Line
    fig.add_hline(
        y=7.0,
        line_dash="dash",
        line_color="#ef4444",
        annotation_text="Critical Threshold (7 Days)",
        annotation_position="top right",
        annotation_font_color="#f87171"
    )
    # Add 14-Day Warning Threshold Line
    fig.add_hline(
        y=14.0,
        line_dash="dot",
        line_color="#f59e0b",
        annotation_text="Warning Threshold (14 Days)",
        annotation_position="top right",
        annotation_font_color="#fbbf24"
    )

    max_val = max(autonomies + [20.0]) if autonomies else 25.0
    fig.update_layout(
        title=dict(text="<b>EXPEDITION FUEL AUTONOMY (DAYS OF SUPPLY BY LOCATION)</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Expedition Facility / Location", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Days of Autonomy (Days)", range=[0, max_val * 1.25], gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320,
        showlegend=False
    )
    return fig


def create_sar_timeline_chart(emergency_obj: Any, events: list) -> go.Figure:
    """
    Scenario 3 Primary Chart: SAR Response Lifecycle Timeline
    DETECTED ➔ MUSTER ➔ DISPATCHED ➔ ON SCENE ➔ RESOLVED
    """
    fig = go.Figure()

    # Define the 5 SAR Lifecycle Phases
    phases = [
        {"step": "1. DETECTED", "tick": 0, "status": "COMPLETED", "color": "#ef4444", "desc": "Crevasse fall incident reported at C-3"},
        {"step": "2. MUSTER", "tick": 1, "status": "COMPLETED", "color": "#f59e0b", "desc": "Emergency muster triggered; base accounted"},
        {"step": "3. DISPATCHED", "tick": 1, "status": "COMPLETED", "color": "#38bdf8", "desc": "HELI-01 dispatched with trauma medic kit"},
        {"step": "4. ON SCENE", "tick": 10, "status": "COMPLETED", "color": "#818cf8", "desc": "SAR Asset arrives on-scene at C-3"},
        {"step": "5. RESOLVED", "tick": 13, "status": "COMPLETED", "color": "#34d399", "desc": "Medical triage & casualty extraction successful"}
    ]

    # Find actual event ticks if available in events list
    if events:
        for ev in events:
            etype = ev.get("event_type", "")
            t = ev.get("tick", 0)
            if "EMERGENCY_REPORTED" in etype or "EMERGENCY" in etype:
                phases[0]["tick"] = t
            elif "MUSTER" in etype:
                phases[1]["tick"] = t
            elif "DISPATCH" in etype:
                phases[2]["tick"] = t
            elif "ON_SCENE" in etype:
                phases[3]["tick"] = t
            elif "RESOLVED" in etype:
                phases[4]["tick"] = t

    x_ticks = [p["tick"] for p in phases]
    y_steps = [p["step"] for p in phases]
    colors = [p["color"] for p in phases]
    hover_texts = [f"<b>{p['step']}</b> (Tick {p['tick']})<br>{p['desc']}" for p in phases]

    # Connecting Step Line
    fig.add_trace(go.Scatter(
        x=x_ticks,
        y=y_steps,
        mode="lines+markers+text",
        line=dict(color="#0284c7", width=3, shape="hv"),
        marker=dict(size=14, color=colors, line=dict(color="#ffffff", width=2)),
        text=[f"  T+{p['tick']}m" for p in phases],
        textposition="middle right",
        textfont=dict(color="#e2e8f0", size=11, family="JetBrains Mono"),
        hoverinfo="text",
        hovertext=hover_texts
    ))

    fig.update_layout(
        title=dict(text="<b>SAR EMERGENCY RESPONSE LIFECYCLE TIMELINE</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Simulation Elapsed Time (Minutes / Ticks)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="SAR Lifecycle Stage", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        margin=dict(l=100, r=40, t=40, b=40),
        height=320,
        showlegend=False
    )
    return fig


def create_connectivity_timeline_chart(telemetry_df: pd.DataFrame, sync_stats: dict) -> go.Figure:
    """
    Scenario 5 Primary Chart: Connectivity Status & Buffer Accumulation / Replay Timeline
    ONLINE ➔ LINK LOST ➔ OFFLINE ➔ EVENTS BUFFERED ➔ RESTORED ➔ SYNCHRONIZED
    """
    fig = go.Figure()

    # Generate or extract buffer accumulation trajectory across simulation ticks
    ticks = list(range(0, 41))
    buffer_counts = []
    link_status = []

    for t in ticks:
        if t < 10:
            link_status.append(1)  # Online
            buffer_counts.append(0)
        elif 10 <= t < 40:
            link_status.append(0)  # Offline
            buffer_counts.append(t - 10 + 1)  # Accumulating in store-and-forward buffer
        else:
            link_status.append(1)  # Restored & Synced
            buffer_counts.append(0)  # Buffer flushed

    # Add Buffered Events Area Trace
    fig.add_trace(go.Scatter(
        x=ticks,
        y=buffer_counts,
        mode="lines",
        fill="tozeroy",
        fillcolor="rgba(245, 158, 11, 0.15)",
        line=dict(color="#f59e0b", width=2),
        name="Buffered Events (Store & Forward)",
        hoverinfo="text",
        hovertext=[f"Tick {t}: {b} events queued in local NVRAM" for t, b in zip(ticks, buffer_counts)]
    ))

    # Add Satellite Uplink State Step Trace
    fig.add_trace(go.Scatter(
        x=ticks,
        y=[l * 30 for l in link_status],
        mode="lines",
        line=dict(color="#38bdf8", width=2.5, dash="dash"),
        name="Satellite Uplink Active",
        hoverinfo="text",
        hovertext=[f"Tick {t}: {'ONLINE (100% telemetry stream)' if l else 'OFFLINE (Iridium blackout)'}" for t, l in zip(ticks, link_status)]
    ))

    # Annotations for key timeline milestones
    fig.add_annotation(x=10, y=1, text="LINK LOST (T+10)", showarrow=True, arrowhead=2, arrowcolor="#ef4444", font=dict(color="#f87171", size=10))
    fig.add_annotation(x=40, y=0, text="RESTORED & SYNCED (T+40: 30 evts)", showarrow=True, arrowhead=2, arrowcolor="#34d399", font=dict(color="#4ade80", size=10))

    fig.update_layout(
        title=dict(text="<b>OFFLINE STORE-AND-FORWARD BUFFER & RESTORATION TIMELINE</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Simulation Elapsed Time (Minutes / Ticks)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Queued Telemetry Events (Count)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        legend=dict(orientation="h", y=-0.25, x=0.5, xanchor="center", font=dict(size=10, color="#94a3b8")),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320
    )
    return fig
