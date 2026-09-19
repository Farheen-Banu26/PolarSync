import plotly.graph_objects as go
import numpy as np
from typing import Dict, Any


def create_polar_operations_map(data: Dict[str, Any]) -> go.Figure:
    """
    Generate an interactive high-resolution Plotly Polar Operations Map
    displaying stations, danger zones, routes, vehicles, emergency incident, and SAR paths.
    """
    fig = go.Figure()
    map_top = data["map_topology"]
    veh_df = data["vehicles_df"]
    emergency = data.get("active_emergency")

    # 1. Plot Base & Camp Routes with Clean Legend Grouping
    for r in map_top["routes"]:
        lats = [wp[0] for wp in r["waypoints"]]
        lons = [wp[1] for wp in r["waypoints"]]
        
        is_emergency_route = "EMERGENCY" in r["id"]
        line_color = "#ef4444" if is_emergency_route else "#0284c7"
        line_dash = "dash" if is_emergency_route else "dot"
        line_width = 3 if is_emergency_route else 2
        route_display_name = f"🚨 {r['name']}" if is_emergency_route else r['name']

        fig.add_trace(go.Scatter(
            x=lons,
            y=lats,
            mode="lines+markers",
            line=dict(color=line_color, width=line_width, dash=line_dash),
            marker=dict(size=4, color=line_color),
            name=route_display_name,
            legendgroup="ROUTES",
            legendgrouptitle_text="<b>ROUTES</b>",
            hoverinfo="text",
            hovertext=f"<b>{r['name']}</b><br>Distance: {r['distance_km']} km",
            showlegend=True
        ))

    # Label mapping for clean, concise map view
    location_short_names = {
        "BASE-MAITRI": ("MAITRI-II", "top left"),
        "CAMP-ALPHA": ("CAMP ALPHA", "top right"),
        "CAMP-ZULU": ("CAMP ZULU", "top right"),
        "CAMP-BRAVO": ("CAMP BRAVO", "bottom left"),
        "EVAC-STATION": ("EVAC OSCAR", "bottom right")
    }

    key_vehicles = {"HELI-01", "VEH-01-SNOWCAT", "VEH-02-SNOWCAT"}
    vehicle_short_names = {
        "HELI-01": ("HELI-01", "top right"),
        "VEH-01-SNOWCAT": ("VEH-01", "bottom right"),
        "VEH-02-SNOWCAT": ("VEH-02", "bottom left"),
        "SKIDOO-01": ("SKIDOO-1", "middle right"),
        "SKIDOO-02": ("SKIDOO-2", "middle left"),
        "BULLY-01": ("BULLY-01", "top center")
    }

    # 2. Plot Danger Zones
    for dz in map_top["danger_zones"]:
        clat, clon = dz["center_lat"], dz["center_lon"]
        radius_deg = dz["radius_km"] / 111.0
        
        # Circle coordinates
        angles = np.linspace(0, 2 * np.pi, 40)
        circle_lats = clat + radius_deg * np.sin(angles)
        circle_lons = clon + (radius_deg / np.cos(np.radians(clat))) * np.cos(angles)
        
        fill_color = "rgba(239, 68, 68, 0.15)" if dz["severity"] == "EXTREME" else "rgba(245, 158, 11, 0.12)"
        border_color = "#ef4444" if dz["severity"] == "EXTREME" else "#f59e0b"
        short_label = "C-3" if "CREVASSE" in dz["id"] else "WHITEOUT"

        fig.add_trace(go.Scatter(
            x=circle_lons,
            y=circle_lats,
            fill="toself",
            fillcolor=fill_color,
            line=dict(color=border_color, width=1.5, dash="dash"),
            name=f"{dz['name']} ({short_label})",
            legendgroup="ZONES",
            legendgrouptitle_text="<b>DANGER ZONES</b>",
            hoverinfo="text",
            hovertext=f"<b>DANGER ZONE: {dz['name']} ({short_label})</b><br>Type: {dz['type']}<br>Radius: {dz['radius_km']} km<br>Severity: {dz['severity']}",
            showlegend=True
        ))

    # 3. Plot Stations & Outposts (Clean non-overlapping positions)
    for loc in map_top["locations"]:
        icon_symbol = "diamond-wide" if loc["type"] == "RESEARCH_BASE" else "square"
        marker_color = "#38bdf8" if loc["type"] == "RESEARCH_BASE" else "#a78bfa"
        marker_size = 14 if loc["type"] == "RESEARCH_BASE" else 10
        short_label, text_pos = location_short_names.get(loc["id"], (loc["id"], "top right"))

        # Only show visible text for primary base and main camps to avoid overlap at base
        show_text = (loc["id"] != "EVAC-STATION")
        text_content = [f" <b>{short_label}</b>"] if show_text else None
        mode_val = "markers+text" if show_text else "markers"

        fig.add_trace(go.Scatter(
            x=[loc["lon"]],
            y=[loc["lat"]],
            mode=mode_val,
            marker=dict(symbol=icon_symbol, size=marker_size, color=marker_color, line=dict(color="#ffffff", width=1.5)),
            text=text_content,
            textposition=text_pos,
            textfont=dict(size=10, color="#f8fafc", family="JetBrains Mono"),
            name=f"Facility: {short_label}",
            hoverinfo="text",
            hovertext=f"<b>{loc['name']}</b> ({short_label})<br>Type: {loc['type']}<br>Coordinates: ({loc['lat']:.4f}, {loc['lon']:.4f})<br>Facilities: {', '.join(loc['facilities'])}",
            showlegend=False
        ))

    # 4. Plot Active Vehicle Fleet Positions
    for _, veh in veh_df.iterrows():
        is_heli = (veh["Type"] == "HELICOPTER")
        is_dispatched = (veh["Status"] == "DISPATCHED_EMERGENCY")
        
        veh_color = "#f43f5e" if is_dispatched else ("#34d399" if is_heli else "#facc15")
        veh_symbol = "triangle-up" if is_heli else "circle"
        veh_size = 13 if (is_heli or is_dispatched) else 10
        
        short_veh_name, text_pos = vehicle_short_names.get(veh["Vehicle ID"], (veh["Vehicle ID"], "bottom right"))
        
        # Only show map text for key assets (HELI-01, VEH-01, VEH-02) to prevent text clutter
        show_text = (veh["Vehicle ID"] in key_vehicles or is_dispatched)
        text_content = [f" {short_veh_name}"] if show_text else None
        mode_val = "markers+text" if show_text else "markers"

        fig.add_trace(go.Scatter(
            x=[veh["Longitude"]],
            y=[veh["Latitude"]],
            mode=mode_val,
            marker=dict(symbol=veh_symbol, size=veh_size, color=veh_color, line=dict(color="#0f172a", width=2)),
            text=text_content,
            textposition=text_pos,
            textfont=dict(size=10, color=veh_color, family="JetBrains Mono"),
            name=f"{veh['Name']} ({short_veh_name})",
            legendgroup="ASSETS",
            legendgrouptitle_text="<b>ASSETS</b>",
            hoverinfo="text",
            hovertext=(
                f"<b>{veh['Name']}</b> ({short_veh_name})<br>"
                f"Type: {veh['Type']}<br>"
                f"Status: {veh['Status']}<br>"
                f"Speed: {veh['Speed (km/h)']} km/h | Heading: {veh['Heading (deg)']}°<br>"
                f"Fuel: {veh['Fuel (%)']}% ({veh['Fuel Remaining (L)']} L)<br>"
                f"Battery: {veh['Battery (%)']}%<br>"
                f"Position: ({veh['Latitude']:.4f}, {veh['Longitude']:.4f})"
            ),
            showlegend=True
        ))

    # 5. Plot Emergency Incident Location if Active
    if emergency:
        elat, elon = emergency.location
        fig.add_trace(go.Scatter(
            x=[elon],
            y=[elat],
            mode="markers+text",
            marker=dict(symbol="star", size=18, color="#ef4444", line=dict(color="#ffffff", width=2)),
            text=[" 🚨 C-3 (EMG)"],
            textposition="top center",
            textfont=dict(size=11, color="#f87171", family="JetBrains Mono", weight="bold"),
            name=f"🚨 Incident: {emergency.id}",
            legendgroup="ZONES",
            hoverinfo="text",
            hovertext=(
                f"<b>EMERGENCY INCIDENT: {emergency.id}</b><br>"
                f"Type: {emergency.incident_type}<br>"
                f"Severity: {emergency.severity.value}<br>"
                f"Location: {emergency.nearest_landmark}<br>"
                f"Status: {emergency.status.value}<br>"
                f"Affected Personnel: {', '.join(emergency.affected_personnel_ids)}"
            ),
            showlegend=True
        ))

    # Dark Polar Aesthetic Layout
    fig.update_layout(
        title=dict(
            text="<b>POLAR OPERATIONAL THEATRE MAP</b> (Antarctic Sector - Larsemann Hills)",
            font=dict(size=14, color="#38bdf8", family="Inter")
        ),
        xaxis=dict(
            title=dict(text="Longitude (°E)", font=dict(color="#94a3b8")),
            gridcolor="rgba(148, 163, 184, 0.1)",
            zerolinecolor="rgba(148, 163, 184, 0.2)",
            tickfont=dict(color="#94a3b8")
        ),
        yaxis=dict(
            title=dict(text="Latitude (°S)", font=dict(color="#94a3b8")),
            gridcolor="rgba(148, 163, 184, 0.1)",
            zerolinecolor="rgba(148, 163, 184, 0.2)",
            tickfont=dict(color="#94a3b8")
        ),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        margin=dict(l=40, r=30, t=50, b=40),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(size=10, color="#94a3b8"),
            bgcolor="rgba(15, 23, 42, 0.8)",
            bordercolor="rgba(56, 189, 248, 0.2)",
            borderwidth=1
        ),
        height=540
    )

    return fig
