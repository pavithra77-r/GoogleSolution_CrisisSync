import hashlib
import streamlit as st
from supabase_helper import supabase

def hash_password(password):
    return hashlib.sha224(password.encode()).hexdigest()

def login_user(email, password):
    try:
        hashed = hash_password(password)
        result = supabase.table("users")\
            .select("*")\
            .eq("email", email)\
            .eq("password_hash", hashed)\
            .eq("is_active", True)\
            .execute()
        if result.data:
            return result.data[0]
        return None
    except Exception as e:
        st.error(f"Login error: {e}")
        return None

def register_user(name, email, password, role, phone):
    try:
        hashed = hash_password(password)
        result = supabase.table("users").insert({
            "name": name,
            "email": email,
            "password_hash": hashed,
            "role": role,
            "phone": phone
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        return None

def get_all_staff():
    result = supabase.table("users")\
        .select("id,name,email,role,phone,is_active,created_at")\
        .neq("role", "guest")\
        .execute()
    return result.data or []

def toggle_staff_status(user_id, current_status):
    supabase.table("users")\
        .update({"is_active": not current_status})\
        .eq("id", user_id)\
        .execute()