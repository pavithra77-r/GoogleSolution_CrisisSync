import streamlit as st

try:
    from supabase_helper import *
except Exception as e:
    st.error(f"❌ Supabase Error: {e}")
    st.stop()

try:
    import folium
    from streamlit_folium import st_folium
except Exception as e:
    st.error(f"❌ Map Error: {e}")
    st.stop()
# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="CrisisSync", page_icon="🚨", layout="wide")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f0f0f; }
[data-testid="stSidebar"] { background: #1a1a1a; }
.stButton>button {
    background: #c0392b; color: white; font-weight: bold;
    border: none; border-radius: 8px; padding: 10px 20px;
    width: 100%; transition: 0.2s;
}
.stButton>button:hover { background: #e74c3c; }
.metric-card {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    border-radius: 12px; padding: 20px; text-align: center;
}
.incident-card {
    background: #1a1a1a; border-left: 4px solid #c0392b;
    border-radius: 8px; padding: 16px; margin-bottom: 12px;
}
.incident-card.resolved { border-left-color: #27ae60; opacity: 0.7; }
.role-badge {
    display: inline-block; padding: 3px 10px;
    border-radius: 20px; font-size: 12px; font-weight: bold;
    margin: 2px; background: #2980b9; color: white;
}
div[data-testid="stForm"] {
    background: #1a1a1a; border-radius: 12px;
    padding: 24px; border: 1px solid #2a2a2a;
}
.guest-sos-btn>button {
    background: linear-gradient(135deg, #c0392b, #922b21) !important;
    font-size: 1.3rem !important;
    padding: 20px !important;
    border-radius: 16px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session State Init ────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = None
if "guest_incident_id" not in st.session_state:
    st.session_state.guest_incident_id = None

# ════════════════════════════════════════════════════════════════════════════
# AUTH PAGES
# ════════════════════════════════════════════════════════════════════════════
def show_auth():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 20px 0;'>
            <h1 style='color:#c0392b; font-size:3rem;'>🚨 CrisisSync</h1>
            <p style='color:#aaa; font-size:1.1rem;'>AI-Powered Emergency Response for Hospitality</p>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])

        # ── LOGIN TAB ────────────────────────────────────────────────────────
        with tab1:
            st.markdown("### Welcome Back")
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="your@email.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submitted = st.form_submit_button("Login →")

                if submitted:
                    if not email or not password:
                        st.error("Please fill in all fields")
                    else:
                        user = login_user(email, password)
                        if user:
                            st.session_state.logged_in = True
                            st.session_state.user = user
                            st.success(f"Welcome back, {user['name']}! 👋")
                            st.rerun()
                        else:
                            st.error("Invalid email or password")

            st.markdown("""
            <div style='background:#1a1a1a; border-radius:8px; padding:12px; margin-top:16px;'>
            <b style='color:#aaa;'>Demo Accounts (password: password123)</b><br>
            <span style='color:#888; font-size:13px;'>
            manager@crisissync.com → Manager<br>
            medical@crisissync.com → Medical Team<br>
            security@crisissync.com → Security<br>
            maintenance@crisissync.com → Maintenance<br>
            guest@crisissync.com → Hotel Guest
            </span>
            </div>
            """, unsafe_allow_html=True)

        # ── REGISTER TAB ─────────────────────────────────────────────────────
        with tab2:
            st.markdown("### Create Account")
            with st.form("register_form"):
                r_name = st.text_input("Full Name", placeholder="Dr. Priya Sharma")
                r_email = st.text_input("Work / Personal Email", placeholder="you@email.com")
                r_phone = st.text_input("Phone Number", placeholder="+91-9000000000")
                r_role = st.selectbox("I am a...", [
                    "guest",           # ← NEW — shown first so guests notice it
                    "staff",
                    "medical_team",
                    "security",
                    "maintenance",
                    "kitchen_staff",
                    "manager"
                ], format_func=lambda x: {
                    "guest":        "🏨 Hotel Guest",
                    "staff":        "👤 Hotel Staff",
                    "medical_team": "🏥 Medical Team",
                    "security":     "🔒 Security",
                    "maintenance":  "🔧 Maintenance",
                    "kitchen_staff":"🍽️ Kitchen Staff",
                    "manager":      "⭐ Manager"
                }.get(x, x))
                r_pass = st.text_input("Password", type="password", placeholder="Min 6 characters")
                r_pass2 = st.text_input("Confirm Password", type="password", placeholder="Repeat password")
                reg_submitted = st.form_submit_button("Create Account →")

                if reg_submitted:
                    if not all([r_name, r_email, r_phone, r_pass, r_pass2]):
                        st.error("Please fill in all fields")
                    elif r_pass != r_pass2:
                        st.error("Passwords do not match!")
                    elif len(r_pass) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        new_user = register_user(r_name, r_email, r_pass, r_role, r_phone)
                        if new_user:
                            st.success("✅ Account created! Please login.")
                        else:
                            st.error("Email already exists or registration failed")


# ════════════════════════════════════════════════════════════════════════════
# GUEST DASHBOARD  ← completely new, self-contained
# ════════════════════════════════════════════════════════════════════════════
def show_guest_app():
    user = st.session_state.user

    # ── Sidebar ───────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:16px 0;'>
            <h2 style='color:#c0392b;'>🚨 CrisisSync</h2>
            <div style='background:#2a2a2a; border-radius:8px; padding:12px; margin-top:8px;'>
                <b style='color:#fff;'>{user['name']}</b><br>
                <span style='color:#c0392b; font-size:13px;'>🏨 Hotel Guest</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background:#1a1a1a; border-radius:8px; padding:12px; margin-top:8px;'>
        <b style='color:#aaa; font-size:13px;'>Need Help?</b><br>
        <span style='color:#888; font-size:12px;'>
        🏥 Medical: Call 112<br>
        🔥 Fire: Pull nearest alarm<br>
        📞 Front Desk: 0
        </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.session_state.guest_incident_id = None
            st.rerun()

    # ── Header ────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1a0000, #2d0a0a);
         border: 1px solid #3d1010; border-radius: 12px;
         padding: 20px 28px; margin-bottom: 24px;'>
        <h2 style='color:#c0392b; margin:0;'>🏨 Guest Emergency Portal</h2>
        <p style='color:#aaa; margin:4px 0 0 0;'>
            Welcome, <b style='color:#fff;'>{user['name']}</b>.
            If you are in danger, use the SOS button below immediately.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # ── 3 Tabs ────────────────────────────────────────────────────────────
    tab_sos, tab_track, tab_map = st.tabs([
        "🆘 Report Emergency",
        "📡 Track My Request",
        "🗺️ Responder Map"
    ])

    # ════════════════════════════════════════════════════════════════
    # GUEST TAB 1 — SOS / Report Emergency
    # ════════════════════════════════════════════════════════════════
    with tab_sos:
        col_left, col_right = st.columns([3, 2])

        with col_left:
            st.markdown("### 🆘 Report an Emergency")
            st.markdown(
                "<p style='color:#aaa;'>Describe what is happening. "
                "Our AI will instantly alert the right staff to help you.</p>",
                unsafe_allow_html=True
            )

            description = st.text_area(
                "What is happening?",
                placeholder="e.g. I fell in the bathroom and cannot get up. Room 204...",
                height=140
            )

            col_a, col_b = st.columns(2)
            with col_a:
                location = st.text_input(
                    "📍 Your Location",
                    placeholder="Room 204 / Pool area / Lobby..."
                )
            with col_b:
                # Pre-fill with guest name
                reported_by = st.text_input("Your Name", value=user["name"])

            # Quick preset buttons
            st.markdown("**Quick presets — tap to fill:**")
            preset_cols = st.columns(3)
            guest_presets = {
                "🤒 I feel sick": "I am feeling very unwell, dizzy and nauseous. Need medical help urgently.",
                "🔥 I see smoke": "I can smell smoke and see it coming from under the door in the corridor.",
                "🔒 Locked out": "I am locked out of my room and cannot get back in. Need assistance.",
                "💧 Water leak": "There is water flooding from the bathroom, it is spreading to the room.",
                "⚡ No power": "My room has completely lost power and the emergency lighting is also off.",
                "🆘 I need help": "I need immediate assistance. Please send someone to my location urgently."
            }
            preset_keys = list(guest_presets.keys())
            for idx, (label, text) in enumerate(guest_presets.items()):
                with preset_cols[idx % 3]:
                    if st.button(label, key=f"gpreset_{idx}"):
                        st.session_state["guest_preset"] = text

            if "guest_preset" in st.session_state:
                st.info(f"Loaded: *{st.session_state['guest_preset'][:80]}...*")

            # Use preset if set
            final_desc = st.session_state.get("guest_preset", description) if not description else description

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🚨 SEND SOS — GET HELP NOW", key="guest_sos"):
                if not final_desc.strip():
                    st.error("Please describe your emergency or use a quick preset above.")
                elif not location.strip():
                    st.error("Please tell us where you are (room number, area).")
                else:
                    with st.spinner("🤖 AI is alerting the right staff for you..."):
                        classification = classify_emergency(final_desc)
                        incident = save_incident(final_desc, reported_by, location, classification)
                        staff_list = get_staff_for_roles(classification["roles_to_notify"])
                        if incident:
                            log_notification(
                                incident["id"],
                                classification["roles_to_notify"],
                                staff_list
                            )
                            # Save incident ID so guest can track it
                            st.session_state.guest_incident_id = incident["id"]

                    st.markdown("""
                    <div style='background:#0d2b0d; border:1px solid #27ae60;
                         border-radius:12px; padding:20px; margin-top:16px;'>
                        <h3 style='color:#27ae60; margin:0;'>✅ Help is on the way!</h3>
                        <p style='color:#aaa; margin:8px 0 0 0;'>
                            The right team has been alerted and is responding.
                            Switch to <b>📡 Track My Request</b> tab to follow live updates.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    sev = classification["severity"]
                    sev_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(sev, "🟡")

                    st.markdown(f"""
                    | | |
                    |---|---|
                    | **Emergency Type** | `{classification['type'].upper()}` |
                    | **Severity** | {sev_color} `{sev.upper()}` |
                    | **Teams Alerted** | {', '.join(classification['roles_to_notify']).replace('_', ' ').title()} |
                    | **Staff Responding** | {len(staff_list)} people |
                    """)

                    if classification.get("sop_steps"):
                        st.markdown("**What to do while help arrives:**")
                        for i, step in enumerate(classification["sop_steps"][:3], 1):
                            st.markdown(f"{i}. {step}")

        with col_right:
            st.markdown("### 📋 Emergency Contacts")
            st.markdown("""
            <div style='background:#1a1a1a; border-radius:10px; padding:16px;'>
            <p style='color:#e74c3c; font-size:1.1rem; margin:0 0 12px 0;'><b>🚨 In life-threatening danger?</b></p>
            <p style='color:#fff; font-size:1.4rem; margin:0 0 4px 0;'>📞 <b>Call 112</b></p>
            <p style='color:#888; font-size:13px; margin:0 0 16px 0;'>National Emergency Number</p>

            <p style='color:#aaa; margin:0 0 4px 0;'><b>🏨 Hotel Front Desk</b></p>
            <p style='color:#fff; font-size:1.2rem; margin:0 0 16px 0;'>📞 Dial <b>0</b> from your room</p>

            <p style='color:#aaa; margin:0 0 4px 0;'><b>🏥 Medical Emergency</b></p>
            <p style='color:#fff; font-size:1.2rem; margin:0 0 16px 0;'>📞 <b>108</b> (Ambulance)</p>

            <p style='color:#aaa; margin:0 0 4px 0;'><b>🔥 Fire Emergency</b></p>
            <p style='color:#fff; font-size:1.2rem; margin:0;'>📞 <b>101</b> (Fire Brigade)</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🛡️ What happens after SOS?")
            st.markdown("""
            <div style='background:#1a1a1a; border-radius:10px; padding:16px;'>
            <div style='display:flex; align-items:flex-start; margin-bottom:12px;'>
                <span style='color:#c0392b; font-size:1.2rem; margin-right:10px;'>1</span>
                <span style='color:#ccc;'>AI reads your message and identifies the emergency type</span>
            </div>
            <div style='display:flex; align-items:flex-start; margin-bottom:12px;'>
                <span style='color:#c0392b; font-size:1.2rem; margin-right:10px;'>2</span>
                <span style='color:#ccc;'>Only the relevant team gets alerted (medical / security / maintenance)</span>
            </div>
            <div style='display:flex; align-items:flex-start; margin-bottom:12px;'>
                <span style='color:#c0392b; font-size:1.2rem; margin-right:10px;'>3</span>
                <span style='color:#ccc;'>Responders see your location and start moving toward you</span>
            </div>
            <div style='display:flex; align-items:flex-start;'>
                <span style='color:#c0392b; font-size:1.2rem; margin-right:10px;'>4</span>
                <span style='color:#ccc;'>Track them live on the Responder Map tab</span>
            </div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # GUEST TAB 2 — Track My Request
    # ════════════════════════════════════════════════════════════════
    with tab_track:
        st.markdown("### 📡 Track Your Emergency Request")

        incident_id = st.session_state.get("guest_incident_id")

        if not incident_id:
            st.info("You haven't submitted an emergency request yet in this session. Use the 🆘 tab to report one.")

            # Let guest manually enter an incident ID if they have one
            st.markdown("---")
            st.markdown("**Already submitted? Enter your request ID:**")
            manual_id = st.text_input("Request ID", placeholder="Paste your incident ID here")
            if st.button("🔍 Look Up") and manual_id:
                st.session_state.guest_incident_id = manual_id.strip()
                st.rerun()
        else:
            # Show the guest's incident live
            col_refresh, _ = st.columns([1, 4])
            with col_refresh:
                if st.button("🔄 Refresh Status"):
                    st.rerun()

            # Fetch the specific incident
            all_inc = get_incidents()
            my_incident = next((i for i in all_inc if str(i.get("id")) == str(incident_id)), None)

            if not my_incident:
                st.warning("Could not find your request. It may have been archived.")
            else:
                status = my_incident.get("status", "active")
                sev = my_incident.get("severity", "medium")
                sev_color = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(sev, "🟡")

                # Status banner
                if status == "resolved":
                    st.markdown("""
                    <div style='background:#0d2b0d; border:2px solid #27ae60;
                         border-radius:12px; padding:20px; text-align:center;'>
                        <h2 style='color:#27ae60; margin:0;'>✅ Your request has been RESOLVED</h2>
                        <p style='color:#aaa; margin:8px 0 0 0;'>The incident has been handled. We hope you are safe.</p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                    <div style='background:#2b0d0d; border:2px solid #c0392b;
                         border-radius:12px; padding:20px; text-align:center;'>
                        <h2 style='color:#e74c3c; margin:0;'>🔴 ACTIVE — Responders are on their way</h2>
                        <p style='color:#aaa; margin:8px 0 0 0;'>
                            Stay calm. Keep this page open. Help is coming.
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Incident details
                d1, d2, d3 = st.columns(3)
                d1.metric("Emergency Type", my_incident.get("type", "—").upper())
                d2.metric("Severity", f"{sev_color} {sev.upper()}")
                d3.metric("Status", status.upper())

                st.markdown("---")

                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("**📋 Your Report**")
                    st.markdown(f"> {my_incident.get('description','—')}")
                    st.markdown(f"**📍 Location reported:** {my_incident.get('location','—')}")
                    ts = my_incident.get("timestamp", "")
                    if ts:
                        st.markdown(f"**🕐 Reported at:** {ts[:16].replace('T', ' ')}")

                with col_b:
                    roles = my_incident.get("roles_notified", [])
                    if roles:
                        st.markdown("**👥 Teams that were alerted:**")
                        for r in roles:
                            st.markdown(f"- ✅ {r.replace('_', ' ').title()}")

                    sop = my_incident.get("sop_steps", [])
                    if sop:
                        st.markdown("**📋 What responders are doing:**")
                        for i, step in enumerate(sop[:4], 1):
                            st.markdown(f"{i}. {step}")

                # Show request ID for reference
                st.markdown("---")
                st.markdown(f"**🔖 Your Request ID:** `{incident_id}`")
                st.caption("Save this ID if you need to look up this request later.")

    # ════════════════════════════════════════════════════════════════
    # GUEST TAB 3 — Responder Map
    # ════════════════════════════════════════════════════════════════
    with tab_map:
        st.markdown("### 🗺️ Where Are the Responders?")
        st.markdown(
            "<p style='color:#aaa;'>Live map showing all on-duty staff locations. "
            "Responders are moving toward your location.</p>",
            unsafe_allow_html=True
        )

        locations = get_staff_locations()

        # Map centered on hotel (Bengaluru example)
        m = folium.Map(
            location=[12.9716, 77.5946],
            zoom_start=17,
            tiles="CartoDB dark_matter"
        )

        # Add a "You are here" marker if guest submitted an incident
        if st.session_state.get("guest_incident_id"):
            folium.Marker(
                location=[12.9716, 77.5946],
                popup=folium.Popup(
                    f"<b>📍 You are here</b><br>Help is on the way!",
                    max_width=200
                ),
                tooltip="📍 Your Location",
                icon=folium.Icon(color="red", icon="home", prefix="glyphicon")
            ).add_to(m)

        role_colors = {
            "medical_team": "red",
            "security":     "blue",
            "maintenance":  "orange",
            "kitchen_staff":"green",
            "manager":      "purple",
            "staff":        "gray"
        }
        role_icons = {
            "medical_team": "plus-sign",
            "security":     "lock",
            "maintenance":  "wrench",
            "kitchen_staff":"cutlery",
            "manager":      "star",
            "staff":        "user"
        }
        role_labels = {
            "medical_team": "🏥 Medical Team",
            "security":     "🔒 Security",
            "maintenance":  "🔧 Maintenance",
            "kitchen_staff":"🍽️ Kitchen Staff",
            "manager":      "⭐ Manager",
            "staff":        "👤 Staff"
        }

        if locations:
            for loc in locations:
                r = loc.get("role", "staff")
                updated = str(loc.get("last_updated", ""))[:16]
                folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    popup=folium.Popup(
                        f"<b>{loc['staff_name']}</b><br>"
                        f"{role_labels.get(r, r)}<br>"
                        f"<span style='color:green;'>● On Duty</span><br>"
                        f"Last seen: {updated}",
                        max_width=200
                    ),
                    tooltip=f"{loc['staff_name']} — {role_labels.get(r, r)}",
                    icon=folium.Icon(
                        color=role_colors.get(r, "gray"),
                        icon=role_icons.get(r, "user"),
                        prefix="glyphicon"
                    )
                ).add_to(m)

            st_folium(m, width=None, height=480)

            # On-duty staff list — simplified for guests
            st.markdown("### 👥 Staff Currently On Duty")
            for loc in locations:
                r = loc.get("role", "staff")
                updated = str(loc.get("last_updated", ""))[:16]
                st.markdown(
                    f"<div style='background:#1a1a1a; border-radius:8px; "
                    f"padding:10px 16px; margin-bottom:8px; display:flex; "
                    f"justify-content:space-between;'>"
                    f"<span style='color:#fff;'><b>{loc['staff_name']}</b> "
                    f"— <span style='color:#aaa;'>{role_labels.get(r, r)}</span></span>"
                    f"<span style='color:#27ae60; font-size:13px;'>● On Duty · {updated}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st_folium(m, width=None, height=480)
            st.info("No staff locations available right now. Staff need to update their location from the app.")

        # What the colours mean
        st.markdown("**🗺️ Map legend:**")
        legend_cols = st.columns(3)
        legend_items = [
            ("🔴 Medical Team", "First aid & medical response"),
            ("🔵 Security", "Safety & access control"),
            ("🟠 Maintenance", "Technical & infrastructure"),
            ("🟢 Kitchen Staff", "Food & dining emergencies"),
            ("🟣 Manager", "Oversight & coordination"),
            ("📍 You", "Your reported location"),
        ]
        for i, (name, desc) in enumerate(legend_items):
            with legend_cols[i % 3]:
                st.markdown(f"**{name}**")
                st.caption(desc)


# ════════════════════════════════════════════════════════════════════════════
# STAFF + MANAGER APP  ← identical to your working version, zero changes
# ════════════════════════════════════════════════════════════════════════════
def show_main_app():
    user = st.session_state.user
    role = user["role"]

    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding:16px 0;'>
            <h2 style='color:#c0392b;'>🚨 CrisisSync</h2>
            <div style='background:#2a2a2a; border-radius:8px; padding:12px; margin-top:8px;'>
                <b style='color:#fff;'>{user['name']}</b><br>
                <span style='color:#c0392b; font-size:13px;'>{role.replace("_"," ").title()}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if role != "manager":
            st.markdown("---")
            st.markdown("**📍 My Location**")
            lat = st.number_input("Latitude", value=12.9716, format="%.4f", key="my_lat")
            lng = st.number_input("Longitude", value=77.5946, format="%.4f", key="my_lng")
            if st.button("📍 Update My Location"):
                update_staff_location(user["id"], user["name"], user["role"], lat, lng)
                st.success("Location updated!")

        st.markdown("---")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()

    st.markdown(f"## 🚨 CrisisSync — Welcome, {user['name']}")

    if role == "manager":
        tabs = st.tabs(["🆘 Report Emergency", "📋 Live Incidents", "🗺️ Staff Map", "📊 Analytics", "🗂️ History", "👥 Staff Management"])
        tab_sos, tab_live, tab_map, tab_analytics, tab_history, tab_staff = tabs
    else:
        tabs = st.tabs(["🆘 Report Emergency", "📋 My Alerts", "🗺️ Team Map"])
        tab_sos, tab_live, tab_map = tabs
        tab_analytics = tab_history = tab_staff = None

    with tab_sos:
        col1, col2 = st.columns([3, 2])
        with col1:
            st.markdown("### 🆘 Trigger Emergency Alert")
            description = st.text_area(
                "Describe the emergency",
                placeholder="e.g. Guest in room 204 collapsed and is not breathing...",
                height=130
            )
            loc_col1, loc_col2 = st.columns(2)
            with loc_col1:
                location = st.text_input("📍 Location", placeholder="Room 204, Pool, Lobby...")
            with loc_col2:
                reported_by = st.text_input("👤 Reported By", value=user["name"])

            if st.button("🚨 TRIGGER SOS ALERT", key="sos_btn"):
                if not description:
                    st.error("Please describe the emergency!")
                else:
                    with st.spinner("🤖 Gemini AI classifying emergency..."):
                        classification = classify_emergency(description)
                    with st.spinner("💾 Saving to database..."):
                        incident = save_incident(description, reported_by, location, classification)
                    with st.spinner("📢 Alerting relevant staff..."):
                        staff_list = get_staff_for_roles(classification["roles_to_notify"])
                        if incident:
                            log_notification(incident["id"], classification["roles_to_notify"], staff_list)

                    sev = classification["severity"]
                    sev_color = {"critical":"🔴","high":"🟠","medium":"🟡","low":"🟢"}.get(sev,"🟡")
                    st.success("✅ Emergency Processed & Staff Alerted!")
                    st.markdown(f"""
                    | Field | Value |
                    |---|---|
                    | **Type** | `{classification['type'].upper()}` |
                    | **Severity** | {sev_color} `{sev.upper()}` |
                    | **Summary** | {classification['summary']} |
                    | **Roles Alerted** | {', '.join(classification['roles_to_notify'])} |
                    | **Staff Notified** | {len(staff_list)} people |
                    """)
                    st.markdown("**📋 AI-Generated SOP Steps:**")
                    for i, step in enumerate(classification["sop_steps"], 1):
                        st.markdown(f"{i}. {step}")

        with col2:
            st.markdown("### ⚡ Quick SOS Presets")
            presets = {
                "🏥 Medical Emergency": "Guest collapsed and is unconscious, needs immediate medical attention",
                "🔥 Fire Alert": "Smoke detected near kitchen, possible fire outbreak",
                "🔒 Security Breach": "Unauthorized person spotted in restricted area near server room",
                "💧 Flood/Leak": "Burst pipe flooding guest room corridor on floor 3",
                "⚡ Power Outage": "Complete power failure in east wing affecting 20 rooms",
                "🍽️ Food Poisoning": "Multiple guests reporting severe stomach pain after dinner"
            }
            for label, desc_text in presets.items():
                if st.button(label, key=f"preset_{label}"):
                    st.session_state["preset_desc"] = desc_text
            if "preset_desc" in st.session_state:
                st.info(f"**Preset loaded:** {st.session_state['preset_desc'][:80]}...")

    with tab_live:
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            search = st.text_input("🔍 Search incidents", placeholder="Search by location, type...")
        with col2:
            status_filter = st.selectbox("Filter by status", ["All", "Active", "Resolved"])
        with col3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 Refresh"):
                st.rerun()

        incidents = get_incidents(status_filter, search)
        total = len(incidents)
        active = len([i for i in incidents if i.get("status") == "active"])
        critical = len([i for i in incidents if i.get("severity") == "critical"])
        resolved = len([i for i in incidents if i.get("status") == "resolved"])

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Incidents", total)
        m2.metric("🔴 Active", active)
        m3.metric("⚠️ Critical", critical)
        m4.metric("✅ Resolved", resolved)
        st.divider()

        if not incidents:
            st.info("No incidents found.")
        else:
            if role != "manager":
                incidents = [i for i in incidents if role in (i.get("roles_notified") or [])]
                if not incidents:
                    st.info("No alerts assigned to your role yet.")

            for inc in incidents:
                sev = inc.get("severity", "medium")
                inc_type = inc.get("type", "general")
                status = inc.get("status", "active")
                sev_color = {"critical":"🔴","high":"🟠","medium":"🟡","low":"🟢"}.get(sev,"🟡")

                with st.expander(
                    f"{sev_color} [{inc_type.upper()}] {inc.get('summary', inc.get('description',''))[:70]}... — {'✅ RESOLVED' if status=='resolved' else '🔴 ACTIVE'}"
                ):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**📍 Location:** {inc.get('location','Unknown')}")
                        st.markdown(f"**👤 Reported by:** {inc.get('reported_by','Unknown')}")
                        st.markdown(f"**⚠️ Severity:** {sev.upper()}")
                        st.markdown(f"**📁 Status:** {status.upper()}")
                    with c2:
                        roles = inc.get("roles_notified", [])
                        if roles:
                            st.markdown(f"**🔔 Roles Alerted:** {', '.join(roles)}")
                        ts = inc.get("timestamp","")
                        if ts:
                            st.markdown(f"**🕐 Time:** {ts[:16].replace('T',' ')}")
                    sop = inc.get("sop_steps", [])
                    if sop:
                        st.markdown("**📋 SOP Steps:**")
                        for i, step in enumerate(sop, 1):
                            st.markdown(f"{i}. {step}")
                    if status != "resolved" and role == "manager":
                        if st.button(f"✅ Mark Resolved", key=f"resolve_{inc['id']}"):
                            resolve_incident(inc["id"])
                            st.success("Incident resolved!")
                            st.rerun()

    with tab_map:
        st.markdown("### 🗺️ Live Staff Location Map")
        st.caption("Staff members update their location from the sidebar.")
        locations = get_staff_locations()
        m = folium.Map(location=[12.9716, 77.5946], zoom_start=16, tiles="CartoDB dark_matter")
        role_colors = {"medical_team":"red","security":"blue","maintenance":"orange","kitchen_staff":"green","manager":"purple","staff":"gray"}
        role_icons = {"medical_team":"plus-sign","security":"lock","maintenance":"wrench","kitchen_staff":"cutlery","manager":"star","staff":"user"}

        if locations:
            for loc in locations:
                r = loc.get("role", "staff")
                folium.Marker(
                    location=[loc["latitude"], loc["longitude"]],
                    popup=folium.Popup(f"<b>{loc['staff_name']}</b><br>Role: {r.replace('_',' ').title()}<br>Updated: {str(loc.get('last_updated',''))[:16]}", max_width=200),
                    tooltip=f"{loc['staff_name']} ({r.replace('_',' ').title()})",
                    icon=folium.Icon(color=role_colors.get(r,"gray"), icon=role_icons.get(r,"user"), prefix="glyphicon")
                ).add_to(m)
        st_folium(m, width=None, height=500)

        if locations:
            st.markdown("### 👥 Staff Currently On Duty")
            df_loc = pd.DataFrame(locations)[["staff_name","role","latitude","longitude","last_updated"]]
            df_loc.columns = ["Name","Role","Lat","Lng","Last Updated"]
            df_loc["Last Updated"] = df_loc["Last Updated"].astype(str).str[:16]
            st.dataframe(df_loc, use_container_width=True)

    if role == "manager" and tab_analytics:
        with tab_analytics:
            st.markdown("### 📊 Incident Analytics Dashboard")
            data = get_analytics()
            if not data:
                st.info("No incident data yet.")
            else:
                df = pd.DataFrame(data)
                col1, col2 = st.columns(2)
                with col1:
                    if "type" in df.columns:
                        type_counts = df["type"].value_counts().reset_index()
                        type_counts.columns = ["Type", "Count"]
                        fig1 = px.pie(type_counts, names="Type", values="Count", title="Incidents by Type", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig1, use_container_width=True)
                with col2:
                    if "severity" in df.columns:
                        sev_counts = df["severity"].value_counts().reset_index()
                        sev_counts.columns = ["Severity","Count"]
                        fig2 = px.bar(sev_counts, x="Severity", y="Count", title="Incidents by Severity", color="Severity", color_discrete_map={"critical":"#e74c3c","high":"#e67e22","medium":"#f39c12","low":"#27ae60"})
                        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig2, use_container_width=True)
                col3, col4 = st.columns(2)
                with col3:
                    if "status" in df.columns:
                        status_counts = df["status"].value_counts().reset_index()
                        status_counts.columns = ["Status","Count"]
                        fig3 = px.pie(status_counts, names="Status", values="Count", title="Active vs Resolved", color_discrete_sequence=["#e74c3c","#27ae60"])
                        fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="white")
                        st.plotly_chart(fig3, use_container_width=True)
                with col4:
                    st.markdown("#### 📈 Key Metrics")
                    total_inc = len(df)
                    resolved_inc = len(df[df["status"]=="resolved"]) if "status" in df.columns else 0
                    resolution_rate = round((resolved_inc/total_inc)*100) if total_inc > 0 else 0
                    critical_inc = len(df[df["severity"]=="critical"]) if "severity" in df.columns else 0
                    st.metric("Total Incidents", total_inc)
                    st.metric("Resolution Rate", f"{resolution_rate}%")
                    st.metric("Critical Incidents", critical_inc)
                    st.metric("Active Incidents", total_inc - resolved_inc)

    if role == "manager" and tab_history:
        with tab_history:
            st.markdown("### 🗂️ Full Incident History")
            col1, col2 = st.columns([3,1])
            with col1:
                search_h = st.text_input("🔍 Search history", placeholder="Search by description, location, type...")
            with col2:
                type_filter = st.selectbox("Filter by type", ["All","medical","fire","intruder","theft","flood","power_outage","food_poisoning","guest_conflict","general"])
            all_incidents = get_incidents(search_query=search_h)
            if type_filter != "All":
                all_incidents = [i for i in all_incidents if i.get("type") == type_filter]
            if not all_incidents:
                st.info("No incidents found.")
            else:
                df_hist = pd.DataFrame(all_incidents)
                cols_to_show = ["timestamp","type","severity","status","location","reported_by","summary"]
                cols_available = [c for c in cols_to_show if c in df_hist.columns]
                df_display = df_hist[cols_available].copy()
                if "timestamp" in df_display.columns:
                    df_display["timestamp"] = df_display["timestamp"].astype(str).str[:16]
                df_display.columns = [c.replace("_"," ").title() for c in df_display.columns]
                st.dataframe(df_display, use_container_width=True, height=400)
                st.caption(f"Showing {len(all_incidents)} incidents")

    if role == "manager" and tab_staff:
        with tab_staff:
            st.markdown("### 👥 Staff Management")
            col1, col2 = st.columns([2,1])
            with col1:
                st.markdown("#### Current Staff")
                staff_list = get_all_staff()
                if staff_list:
                    for s in staff_list:
                        with st.expander(f"{'🟢' if s['is_active'] else '🔴'} {s['name']} — {s['role'].replace('_',' ').title()}"):
                            sc1, sc2 = st.columns(2)
                            with sc1:
                                st.markdown(f"**Email:** {s['email']}")
                                st.markdown(f"**Phone:** {s.get('phone','N/A')}")
                                st.markdown(f"**Role:** {s['role'].replace('_',' ').title()}")
                            with sc2:
                                st.markdown(f"**Status:** {'✅ Active' if s['is_active'] else '❌ Inactive'}")
                                st.markdown(f"**Joined:** {str(s.get('created_at',''))[:10]}")
                            if st.button(f"{'🔴 Deactivate' if s['is_active'] else '🟢 Activate'}", key=f"toggle_{s['id']}"):
                                toggle_staff_status(s["id"], s["is_active"])
                                st.rerun()
            with col2:
                st.markdown("#### ➕ Add New Staff")
                with st.form("add_staff_form"):
                    ns_name = st.text_input("Full Name")
                    ns_email = st.text_input("Email")
                    ns_phone = st.text_input("Phone")
                    ns_role = st.selectbox("Role", ["staff","medical_team","security","maintenance","kitchen_staff","manager"])
                    ns_pass = st.text_input("Temporary Password", type="password", value="password123")
                    add_btn = st.form_submit_button("➕ Add Staff")
                    if add_btn:
                        if not all([ns_name, ns_email, ns_role]):
                            st.error("Name, email, and role are required")
                        else:
                            new_s = register_user(ns_name, ns_email, ns_pass, ns_role, ns_phone)
                            if new_s:
                                st.success(f"✅ {ns_name} added!")
                                st.rerun()
                            else:
                                st.error("Email already exists")


# ════════════════════════════════════════════════════════════════════════════
# ROUTER  ← the only new logic: guests go to show_guest_app()
# ════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    show_auth()
elif st.session_state.user["role"] == "guest":
    show_guest_app()
else:
    show_main_app()