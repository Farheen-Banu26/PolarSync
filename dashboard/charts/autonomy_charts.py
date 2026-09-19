import plotly.graph_objects as go
import pandas as pd


def create_autonomy_bar_chart(inventory_df: pd.DataFrame) -> go.Figure:
    """
    Bar chart comparing Days of Autonomy against Resupply Window and Safety Buffers.
    """
    fig = go.Figure()

    if inventory_df is None or inventory_df.empty:
        fig.update_layout(
            title=dict(text="<b>DAYS OF AUTONOMY BY INVENTORY CATEGORY (No Data)</b>", font=dict(size=13, color="#38bdf8")),
            paper_bgcolor="#0b0f19",
            plot_bgcolor="#0f172a",
            font=dict(family="Inter", color="#e2e8f0"),
            height=320
        )
        return fig

    categories = inventory_df["Category"].tolist() if "Category" in inventory_df.columns else [f"Item {i+1}" for i in range(len(inventory_df))]
    doa_values = [float(v) for v in inventory_df["Days of Autonomy"].tolist()] if "Days of Autonomy" in inventory_df.columns else [0.0] * len(inventory_df)
    resupply_windows = [float(v) for v in inventory_df["Resupply Window (days)"].tolist()] if "Resupply Window (days)" in inventory_df.columns else []
    risks = inventory_df["Resupply Risk"].tolist() if "Resupply Risk" in inventory_df.columns else []

    # Color code bars based on risk level
    risk_colors = {
        "LOW_SAFE": "#22c55e",
        "MODERATE": "#eab308",
        "HIGH": "#f97316",
        "CRITICAL": "#ef4444"
    }
    bar_colors = [risk_colors.get(r, "#38bdf8") for r in risks]

    fig.add_trace(go.Bar(
        x=categories,
        y=doa_values,
        name="Days of Autonomy",
        marker=dict(color=bar_colors, line=dict(color="rgba(255, 255, 255, 0.2)", width=1)),
        text=[f"{v:.1f}d ({r})" if r else f"{v:.1f}d" for v, r in zip(doa_values, risks if len(risks) == len(doa_values) else [""]*len(doa_values))],
        textposition="outside",
        textfont=dict(color="#f8fafc", size=10, family="JetBrains Mono")
    ))

    # Add resupply window marker line
    if resupply_windows:
        window_val = resupply_windows[0]
        fig.add_hline(
            y=window_val,
            line_dash="dash",
            line_color="#ef4444",
            annotation_text=f"Resupply Window ({window_val:.0f} Days)",
            annotation_position="top right",
            annotation_font_color="#f87171"
        )

    fig.update_layout(
        title=dict(text="<b>DAYS OF AUTONOMY BY INVENTORY CATEGORY</b>", font=dict(size=13, color="#38bdf8")),
        xaxis=dict(title="Resource Category", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        yaxis=dict(title="Days of Autonomy (DoA)", gridcolor="rgba(148, 163, 184, 0.1)", tickfont=dict(color="#94a3b8")),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        font=dict(family="Inter", color="#e2e8f0"),
        margin=dict(l=40, r=20, t=40, b=40),
        height=320,
        showlegend=False
    )
    return fig
