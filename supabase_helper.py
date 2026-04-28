import os
from supabase import create_client
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

supabase = create_client(
    os.environ.get("SUPABASE_URL"),
    os.environ.get("SUPABASE_KEY")
)

def save_incident(description, reported_by, location, classification):
    result = supabase.table("incidents").insert({
        "description": description,
        "reported_by": reported_by or "Unknown",
        "location": location or "Unknown",
        "type": classification["type"],
        "severity": classification["severity"],
        "summary": classification["summary"],
        "sop_steps": classification["sop_steps"],
        "roles_notified": classification["roles_to_notify"],
        "status": "active"
    }).execute()
    return result.data[0] if result.data else None

def get_staff_for_roles(roles):
    result = supabase.table("users").select("*").in_("role", roles).eq("is_active", True).execute()
    return result.data or []

def log_notification(incident_id, roles, staff_list):
    supabase.table("notifications").insert({
        "incident_id": incident_id,
        "roles_notified": roles,
        "staff_notified": [{"name": s["name"], "role": s["role"]} for s in staff_list]
    }).execute()

def get_incidents(status_filter=None, search_query=None):
    query = supabase.table("incidents").select("*").order("timestamp", desc=True).limit(50)
    if status_filter and status_filter != "All":
        query = query.eq("status", status_filter.lower())
    result = query.execute()
    data = result.data or []
    if search_query:
        data = [i for i in data if search_query.lower() in (i.get("description","") + i.get("summary","") + i.get("location","")).lower()]
    return data

def resolve_incident(incident_id):
    supabase.table("incidents").update({
        "status": "resolved",
        "resolved_at": datetime.utcnow().isoformat()
    }).eq("id", incident_id).execute()

def get_analytics():
    incidents = supabase.table("incidents").select("type,severity,status,timestamp").execute().data or []
    return incidents

def update_staff_location(user_id, name, role, lat, lng):
    existing = supabase.table("staff_locations").select("id").eq("user_id", user_id).execute()
    if existing.data:
        supabase.table("staff_locations").update({
            "latitude": lat, "longitude": lng,
            "last_updated": datetime.utcnow().isoformat(),
            "is_on_duty": True
        }).eq("user_id", user_id).execute()
    else:
        supabase.table("staff_locations").insert({
            "user_id": user_id, "staff_name": name,
            "role": role, "latitude": lat, "longitude": lng
        }).execute()

def get_staff_locations():
    result = supabase.table("staff_locations").select("*").eq("is_on_duty", True).execute()
    return result.data or []