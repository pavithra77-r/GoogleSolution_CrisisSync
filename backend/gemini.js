const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

// This maps emergency types to which staff roles should be alerted
const ROLE_MAPPING = {
  medical: ["medical_team", "manager"],
  fire: ["security", "maintenance", "manager"],
  intruder: ["security", "manager"],
  theft: ["security", "manager"],
  flood: ["maintenance", "manager"],
  power_outage: ["maintenance", "manager"],
  food_poisoning: ["medical_team", "kitchen_staff", "manager"],
  guest_conflict: ["security", "manager"],
  general: ["manager"],
};

async function classifyEmergency(description) {
  try {
    const model = genAI.getGenerativeModel({ model: "gemini-1.5-flash" });

    const prompt = `
You are an emergency classification AI for a hotel/resort.
Analyze this emergency description and respond ONLY with a JSON object.

Emergency description: "${description}"

Respond with exactly this JSON format (no extra text):
{
  "type": "one of: medical, fire, intruder, theft, flood, power_outage, food_poisoning, guest_conflict, general",
  "severity": "one of: low, medium, high, critical",
  "sop_steps": ["step 1", "step 2", "step 3", "step 4", "step 5"],
  "summary": "one line summary of the emergency"
}
    `;

    const result = await model.generateContent(prompt);
    const text = result.response.text();

    // Clean and parse the JSON
    const cleaned = text.replace(/```json|```/g, "").trim();
    const parsed = JSON.parse(cleaned);

    // Add the roles that need to be notified
    parsed.roles_to_notify = ROLE_MAPPING[parsed.type] || ROLE_MAPPING["general"];

    return parsed;
  } catch (error) {
    console.error("Gemini error:", error);
    // Fallback if AI fails
    return {
      type: "general",
      severity: "medium",
      summary: description,
      sop_steps: ["Alert manager", "Assess situation", "Take action", "Document incident"],
      roles_to_notify: ["manager"],
    };
  }
}

module.exports = { classifyEmergency };