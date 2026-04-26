import os
from supabase import create_client
from dotenv import load_dotenv

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
    result = supabase.table("staff").select("*").in_("role", roles).execute()
    return result.data or []

def log_notification(incident_id, roles, staff_list):
    supabase.table("notifications").insert({
        "incident_id": incident_id,
        "roles_notified": roles,
        "staff_notified": [{"name": s["name"], "role": s["role"]} for s in staff_list]
    }).execute()

def get_incidents():
    result = supabase.table("incidents").select("*").order("timestamp", desc=True).limit(20).execute()
    return result.data or []

def resolve_incident(incident_id):
    from datetime import datetime
    supabase.table("incidents").update({
        "status": "resolved",
        "resolved_at": datetime.utcnow().isoformat()
    }).eq("id", incident_id).execute()