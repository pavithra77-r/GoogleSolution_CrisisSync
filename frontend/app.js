// IMPORTANT: Replace this with your actual Antigravity backend URL
const API_URL = "http://localhost:3000";
// When deployed, it'll look like: "https://your-project.antigravity.dev"

async function reportEmergency() {
  const description = document.getElementById("emergencyDesc").value.trim();
  const reportedBy = document.getElementById("reportedBy").value.trim();
  const location = document.getElementById("location").value.trim();
  const btn = document.getElementById("sosBtn");
  const resultBox = document.getElementById("sosResult");

  if (!description) {
    alert("Please describe the emergency!");
    return;
  }

  // Disable button while processing
  btn.disabled = true;
  btn.textContent = "⏳ Processing...";
  resultBox.style.display = "none";

  try {
    const response = await fetch(`${API_URL}/api/emergency`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ description, reported_by: reportedBy, location }),
    });

    const data = await response.json();

    if (data.success) {
      const c = data.classification;
      resultBox.style.display = "block";
      resultBox.innerHTML = `
        <strong>✅ Emergency Processed!</strong><br><br>
        <span class="badge badge-type">${c.type.toUpperCase()}</span>
        <span class="badge badge-${c.severity}">${c.severity.toUpperCase()}</span><br><br>
        <strong>Summary:</strong> ${c.summary}<br><br>
        <strong>Roles Alerted:</strong> ${c.roles_to_notify.join(", ")}<br>
        <strong>Staff Notified:</strong> ${data.notification_result.notified} people<br><br>
        <strong>SOP Steps:</strong>
        <ol class="sop-list">${c.sop_steps.map(s => `<li>${s}</li>`).join("")}</ol>
      `;

      // Clear the form
      document.getElementById("emergencyDesc").value = "";
    } else {
      resultBox.style.display = "block";
      resultBox.innerHTML = `❌ Error: ${data.error}`;
    }
  } catch (error) {
    resultBox.style.display = "block";
    resultBox.innerHTML = `❌ Could not connect to server. Make sure backend is running.<br>${error.message}`;
  } finally {
    btn.disabled = false;
    btn.textContent = "🚨 TRIGGER SOS ALERT";
  }
}

async function loadIncidents() {
  const list = document.getElementById("incidentsList");
  list.innerHTML = "<p style='color:#888;'>Loading...</p>";

  try {
    const response = await fetch(`${API_URL}/api/incidents`);
    const data = await response.json();

    if (data.incidents.length === 0) {
      list.innerHTML = "<p style='color:#888;'>No incidents yet.</p>";
      return;
    }

    list.innerHTML = data.incidents.map(inc => `
      <div class="incident-item ${inc.status === 'resolved' ? 'resolved' : ''}" id="inc-${inc.id}">
        <span class="badge badge-type">${inc.type || 'general'}</span>
        <span class="badge badge-${inc.severity || 'medium'}">${(inc.severity || 'medium').toUpperCase()}</span>
        ${inc.status === 'resolved' ? '<span class="badge" style="background:#27ae60;">RESOLVED</span>' : ''}<br>
        <strong>${inc.summary || inc.description}</strong><br>
        <small style="color:#888;">📍 ${inc.location || 'Unknown'} &nbsp;|&nbsp; 👤 ${inc.reported_by || 'Unknown'}</small><br>
        <small style="color:#666;">Roles alerted: ${(inc.roles_notified || []).join(", ")}</small>
        ${inc.sop_steps ? `
          <ol class="sop-list">${inc.sop_steps.map(s => `<li>${s}</li>`).join("")}</ol>
        ` : ""}
        ${inc.status !== 'resolved' ? `
          <button class="resolve-btn" onclick="resolveIncident('${inc.id}')">✅ Mark Resolved</button>
        ` : ""}
      </div>
    `).join("");
  } catch (error) {
    list.innerHTML = `<p style='color:#e74c3c;'>Error loading incidents: ${error.message}</p>`;
  }
}

async function resolveIncident(id) {
  try {
    await fetch(`${API_URL}/api/incidents/${id}/resolve`, { method: "PATCH" });
    loadIncidents(); // Refresh the list
  } catch (error) {
    alert("Could not resolve incident: " + error.message);
  }
}

// Auto-load incidents on page open
loadIncidents();