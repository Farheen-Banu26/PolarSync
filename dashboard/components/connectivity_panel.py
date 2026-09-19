import streamlit as st
from typing import Dict, Any


def render_connectivity_panel(data: Dict[str, Any]):
    """
    Render Satellite Uplink & Offline Store-and-Forward Queue Panel.
    """
    sc_idx = data["scenario_index"]
    net_status = data["network_status"]
    queued = data.get("total_queued_events", 0)
    sync_done = data.get("sync_completed", False)

    st.markdown('<div class="panel-header">🛰️ Satellite Telemetry Uplink & Store-and-Forward Sync</div>', unsafe_allow_html=True)

    if sc_idx == 5 or sync_done:
        # Scenario 5 Offline Sync Flow Stepper
        stepper_html = (
            '<div class="timeline-container">'
            '<div class="timeline-step"><div class="step-circle step-active">1</div><div class="step-label">ONLINE<br>(Tick 01-09)</div></div>'
            '<div class="timeline-step"><div class="step-circle step-active" style="background: #ef4444; border-color: #ef4444;">2</div><div class="step-label">LINK SEVERED<br>(Tick 10)</div></div>'
            '<div class="timeline-step"><div class="step-circle step-active" style="background: #f59e0b; border-color: #f59e0b;">3</div><div class="step-label">OFFLINE OPS<br>(Tick 10-39)</div></div>'
            '<div class="timeline-step"><div class="step-circle step-active" style="background: #38bdf8; border-color: #38bdf8;">4</div><div class="step-label">30 EVENTS QUEUED<br>(Local FIFO Buffer)</div></div>'
            '<div class="timeline-step"><div class="step-circle step-active" style="background: #0284c7; border-color: #0284c7;">5</div><div class="step-label">LINK RESTORED<br>(Tick 40)</div></div>'
            '<div class="timeline-step"><div class="step-circle step-active" style="background: #22c55e; border-color: #22c55e;">6</div><div class="step-label">SYNC COMPLETE<br>(Queue Flushed: 0)</div></div>'
            '</div>'
        )
        st.markdown(stepper_html, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">CURRENT SATELLITE STATUS</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: {'#4ade80' if net_status == 'ONLINE' else '#f87171'}; font-family: 'JetBrains Mono'; margin-top: 2px;">
                {net_status}
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Primary Base Transponder Lock</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        buffer_display = f"{queued} Events Buffered ➔ {queued} Synchronized" if queued > 0 else "0 Events Queued (Direct Uplink)"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">LOCAL EVENT BUFFER (FIFO)</div>
            <div style="font-size: 1.15rem; font-weight: 700; color: #38bdf8; font-family: 'JetBrains Mono'; margin-top: 2px;">
                {buffer_display}
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Store-and-Forward Zero Data Loss</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        sync_label = "SYNCHRONIZED (100%)" if sync_done or net_status == "ONLINE" else "WAITING UPLINK"
        sync_color = "#4ade80" if sync_done or net_status == "ONLINE" else "#f59e0b"
        st.markdown(f"""
        <div style="background: rgba(15, 23, 42, 0.7); border: 1px solid rgba(56, 189, 248, 0.2); border-radius: 8px; padding: 14px;">
            <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 600;">CENTRAL REGISTRY RECONCILIATION</div>
            <div style="font-size: 1.4rem; font-weight: 700; color: {sync_color}; font-family: 'JetBrains Mono'; margin-top: 2px;">
                {sync_label}
            </div>
            <div style="font-size: 0.75rem; color: #64748b; margin-top: 4px;">Audit Trail Verified</div>
        </div>
        """, unsafe_allow_html=True)
