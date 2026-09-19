import streamlit as st
from typing import List
from src.models.alert import Alert


def render_alerts_panel(alerts: List[Alert]):
    """
    Render categorized real-time alert stream.
    """
    st.markdown('<div class="panel-header">🔔 Mission Alerts & Anomaly Feed</div>', unsafe_allow_html=True)

    if not alerts:
        st.markdown("""
        <div style="background: rgba(34, 197, 94, 0.08); border: 1px solid rgba(34, 197, 94, 0.2); border-radius: 8px; padding: 12px 16px; color: #4ade80; font-size: 0.88rem;">
            ✅ <b>ALL SYSTEMS NOMINAL</b>: No critical anomalies or threshold breaches active.
        </div>
        """, unsafe_allow_html=True)
        return

    for alert in alerts:
        sev = alert.severity.value
        css_class = "alert-item-critical" if sev == "CRITICAL" else ("alert-item-warning" if sev == "WARNING" else "alert-item-info")
        badge_color = "#ef4444" if sev == "CRITICAL" else ("#f59e0b" if sev == "WARNING" else "#38bdf8")

        st.markdown(f"""
        <div class="{css_class}">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                <span style="font-weight: 700; color: {badge_color}; font-size: 0.85rem;">
                    [{sev}] {alert.category.value}
                </span>
                <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #94a3b8;">
                    Tick {alert.tick} | Source: {alert.source_entity_id}
                </span>
            </div>
            <div style="font-weight: 600; color: #f8fafc; font-size: 0.95rem;">{alert.title}</div>
            <div style="color: #cbd5e1; font-size: 0.82rem; margin-top: 2px;">{alert.message}</div>
        </div>
        """, unsafe_allow_html=True)
