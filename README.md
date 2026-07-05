# 🚨 CrisisSync — AI-Powered Emergency Response for Hospitality

CrisisSync is a role-based emergency response platform built for hotels and hospitality venues. Guests and staff report incidents in plain language, Gemini AI instantly classifies the emergency type and severity, alerts the right team, and everyone can track the response live until it's resolved.

**🔗 Live Demo:** _add your Streamlit app URL here_

---

## 📌 Problem Statement

In hotels, hospitals, and large venues, emergencies are still reported by phone or word-of-mouth. Front desk staff manually decide who to call, costing precious minutes during a crisis. Guests often don't know who to alert or where help currently is, and there's no live visibility into staff location, incident status, or response history.

## 💡 Solution

CrisisSync gives every guest a one-tap SOS portal and every staff role (medical, security, maintenance, kitchen, manager) a live dashboard. An AI layer (Google Gemini) reads free-text incident descriptions, classifies them, drafts SOP steps, and automatically notifies only the relevant team — cutting out manual triage entirely.

---

## ✨ Key Features

### For Guests
- 🆘 One-tap SOS reporting with quick presets (medical, fire, lockout, water leak, power outage)
- 📡 **Track My Request** — live status (Active/Resolved) with a unique request ID
- 🗺️ **Responder Map** — see on-duty staff moving toward their location in real time
- 📞 Always-visible emergency contacts (112 / 108 / 101 / front desk)

### For Staff & Managers
- 🆘 Trigger emergency alerts with role-specific quick presets
- 📋 Live Incidents / My Alerts — filter by status, view AI severity + SOP steps, mark resolved
- 🗺️ Team Map — live staff locations color-coded by role
- 📊 **Analytics Dashboard** (Manager only) — incident type/severity breakdowns, resolution rate
- 🗂️ Full incident history with search & filters
- 👥 Staff management — add, activate/deactivate accounts and roles

### AI-Powered Core
- 🤖 **Gemini AI** classifies each report into an emergency type (medical, fire, intruder, theft, flood, power outage, food poisoning, guest conflict, general) and a severity level (critical/high/medium/low)
- 📋 Auto-generates step-by-step SOP (Standard Operating Procedure) instructions for responders
- 🔀 Smart routing — notifies only the relevant role(s) instead of broadcasting to everyone

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / App Framework | [Streamlit](https://streamlit.io/) |
| Language | Python |
| AI / Emergency Classification | Google Gemini API |
| Database & Auth | [Supabase](https://supabase.com/) (Postgres) |
| Maps | Folium + streamlit-folium |
| Analytics & Charts | Plotly |
| Data Handling | Pandas |
| Hosting | Streamlit Community Cloud |

---

## 🏗️ Architecture / How It Works

1. **Report** — A guest or staff member describes the emergency in plain language and shares their location.
2. **Classify** — Gemini AI reads the text, determines the emergency type and severity, and drafts SOP steps.
3. **Alert** — The relevant team(s) (medical, security, maintenance, manager) are notified instantly.
4. **Track** — Everyone follows live responder locations and incident status via the map and tracking tabs, until the incident is marked resolved.

```
app.py               → Main Streamlit application (auth, guest & staff dashboards, routing)
auth_helper.py       → User registration & login logic
gemini_helper.py     → Gemini AI integration for emergency classification & SOP generation
supabase_helper.py   → Database operations (incidents, staff, locations, notifications)
requirements.txt     → Python dependencies
runtime.txt          → Python runtime version for deployment
```

---

## 🚀 Getting Started (Run Locally)

### Prerequisites
- Python 3.9+
- A [Supabase](https://supabase.com/) project (URL + API key)
- A [Google Gemini API key](https://ai.google.dev/)

### Installation

```bash
# Clone the repository
git clone https://github.com/pavithra77-r/GoogleSolution_CrisisSync.git
cd GoogleSolution_CrisisSync

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory with:

```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key
GEMINI_API_KEY=your_gemini_api_key
```

### Run the app

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

### Demo Accounts

| Email | Role | Password |
|---|---|---|
| manager@crisissync.com | Manager | password123 |
| medical@crisissync.com | Medical Team | password123 |
| security@crisissync.com | Security | password123 |
| maintenance@crisissync.com | Maintenance | password123 |
| guest@crisissync.com | Hotel Guest | password123 |

---

## 🌐 Deployment

This app is deployed on **Streamlit Community Cloud**, so it runs on Streamlit's own servers — anyone can open the live app link at any time without needing your machine to be running. Running `streamlit run app.py` locally is only needed if you want to develop or test on your own computer.

---

## 🔮 Future Scope

- Push/SMS notifications instead of in-app alerts only
- GPS-based automatic location detection for guests
- Multi-language support for international guests
- Multi-property support for hotel chains with centralized analytics

---

## 🙋 Author

**Pavithra R**
Built as part of a Google Solution Challenge submission.

---

