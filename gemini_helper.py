import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

ROLE_MAPPING = {
    "medical": ["medical_team", "manager"],
    "fire": ["security", "maintenance", "manager"],
    "intruder": ["security", "manager"],
    "theft": ["security", "manager"],
    "flood": ["maintenance", "manager"],
    "power_outage": ["maintenance", "manager"],
    "food_poisoning": ["medical_team", "kitchen_staff", "manager"],
    "guest_conflict": ["security", "manager"],
    "general": ["manager"],
}

def classify_emergency(description):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are an emergency classification AI for a hotel/resort.
Analyze this emergency and respond ONLY with a JSON object, no extra text.

Emergency: "{description}"

Respond with exactly this format:
{{
  "type": "one of: medical, fire, intruder, theft, flood, power_outage, food_poisoning, guest_conflict, general",
  "severity": "one of: low, medium, high, critical",
  "sop_steps": ["step 1", "step 2", "step 3", "step 4", "step 5"],
  "summary": "one line summary"
}}
"""
        response = model.generate_content(prompt)
        text = response.text.strip()

        # Clean markdown if present
        text = text.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(text)
        parsed["roles_to_notify"] = ROLE_MAPPING.get(parsed["type"], ["manager"])
        return parsed

    except Exception as e:
        print(f"Gemini error: {e}")
        return {
            "type": "general",
            "severity": "medium",
            "summary": description,
            "sop_steps": ["Alert manager", "Assess situation", "Take action", "Document incident"],
            "roles_to_notify": ["manager"]
        }