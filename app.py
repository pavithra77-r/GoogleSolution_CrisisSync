import streamlit as st
from gemini_helper import classify_emergency
from supabase_helper import (
    save_incident, get_staff_for_roles,
    log_notification, get_incidents, resolve_incident
)

# ── Page config ──────────────────────────────────────────
st.set_page_config(
    page_title="CrisisSync",
    page_icon="🚨",
    layout="wide"
)

# ── Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
.main { background-color: #0f0f0f; }
.stButton>button {
    background-color: #c0392b;
    color: white;
    font-weight: bold;
    width: 100%;
    padding: 12px;
    font-size: 16px;
    border-radius: 8px;
    border: none;
}
.stButton>button:hover { background-color: #e74c3c; }
.severity-critical { color: #e74c3c; font-weight: bold; }
.severity-high { color: #e67e22; font-weight: bold; }
.severity-medium { color: #f39c12; font-weight: bold; }
.severity-low { color: #27ae60; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────
st.markdown("# 🚨 CrisisSync")
st.markdown("### Accelerated Emergency Response for Hospitality")
st.divider()

# ── Two column layout ────────────────────────────────────
col1, col2 = st.columns([1, 1])

# ── LEFT: Report Emergency ───────────────────────────────
with col1:
    st.markdown("## 🆘 Report Emergency")

    description = st.text_area(
        "Describe the emergency",
        placeholder="e.g. Guest in room 204 collapsed and is not breathing...",
        height=120
    )
    reported_by = st.text_input("Your name / Staff ID", placeholder="e.g. Front Desk - Riya")
    location = st.text_input("Location", placeholder="e.g. Room 204, Lobby, Pool Area")

    if st.button("🚨 TRIGGER SOS ALERT"):
        if not description:
            st.error("Please describe the emergency!")
        else:
            with st.spinner("🤖 Gemini AI is classifying the emergency..."):
                classification = classify_emergency(description)

            with st.spinner("💾 Saving to database..."):
                incident = save_incident(description, reported_by, location, classification)

            with st.spinner("📢 Notifying relevant staff..."):
                staff_list = get_staff_for_roles(classification["roles_to_notify"])
                if incident:
                    log_notification(incident["id"], classification["roles_to_notify"], staff_list)

            # Show result
            severity = classification["severity"]
            severity_colors = {
                "critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"
            }
            emoji = severity_colors.get(severity, "🟡")

            st.success("✅ Emergency Processed!")

            st.markdown(f"""
**Type:** `{classification['type'].upper()}`  
**Severity:** {emoji} `{severity.upper()}`  
**Summary:** {classification['summary']}
            """)

            st.markdown("**🏥 Roles Alerted:**")
            for role in classification["roles_to_notify"]:
                st.markdown(f"- `{role}`")

            st.markdown("**👥 Staff Notified:**")
            if staff_list:
                for staff in staff_list:
                    st.markdown(f"- {staff['name']} ({staff['role']})")
            else:
                st.warning("No staff found for these roles in database")

            st.markdown("**📋 SOP Steps:**")
            for i, step in enumerate(classification["sop_steps"], 1):
                st.markdown(f"{i}. {step}")

# ── RIGHT: Live Incidents Dashboard ─────────────────────
with col2:
    st.markdown("## 📋 Live Incidents")

    if st.button("🔄 Refresh Incidents"):
        st.rerun()

    incidents = get_incidents()

    if not incidents:
        st.info("No incidents yet. Report one to get started!")
    else:
        for inc in incidents:
            severity = inc.get("severity", "medium")
            inc_type = inc.get("type", "general")
            status = inc.get("status", "active")

            color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(severity, "🟡")
            status_icon = "✅" if status == "resolved" else "🔴"

            with st.expander(f"{color} {inc_type.upper()} — {inc.get('summary', inc.get('description', ''))[:60]}... {status_icon}"):
                st.markdown(f"**Severity:** {severity.upper()}")
                st.markdown(f"**Status:** {status.upper()}")
                st.markdown(f"**Location:** {inc.get('location', 'Unknown')}")
                st.markdown(f"**Reported by:** {inc.get('reported_by', 'Unknown')}")

                roles = inc.get("roles_notified", [])
                if roles:
                    st.markdown(f"**Roles alerted:** {', '.join(roles)}")

                sop = inc.get("sop_steps", [])
                if sop:
                    st.markdown("**SOP Steps:**")
                    for i, step in enumerate(sop, 1):
                        st.markdown(f"{i}. {step}")

                if status != "resolved":
                    if st.button(f"✅ Resolve", key=f"resolve_{inc['id']}"):
                        resolve_incident(inc["id"])
                        st.success("Marked as resolved!")
                        st.rerun()