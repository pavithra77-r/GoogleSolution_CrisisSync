const { supabase } = require("./supabase");

async function sendAlertToRoles(incidentId, roles, incidentData) {
  try {
    // Get staff members with matching roles from Supabase
    const { data: staffList, error } = await supabase
      .from("staff")
      .select("*")
      .in("role", roles);

    if (error) throw error;

    if (!staffList || staffList.length === 0) {
      console.log("No staff found for roles:", roles);
      return { notified: 0 };
    }

    // Log which staff were notified
    // (In real app, you'd send SMS/email here via Novu or Twilio)
    console.log("📢 Notifying staff:");
    staffList.forEach(s => console.log(`  → ${s.name} (${s.role})`));

    // Save notification log to Supabase
    await supabase.from("notifications").insert({
      incident_id: incidentId,
      roles_notified: roles,
      staff_notified: staffList.map(s => ({ id: s.id, name: s.name, role: s.role })),
    });

    return {
      notified: staffList.length,
      staff: staffList.map(s => ({ name: s.name, role: s.role })),
    };
  } catch (error) {
    console.error("Notification error:", error);
    return { notified: 0, error: error.message };
  }
}

module.exports = { sendAlertToRoles };