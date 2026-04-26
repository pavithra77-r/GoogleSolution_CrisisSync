require("dotenv").config();
process.on("uncaughtException", (err) => {
    console.log("❌ UNCAUGHT ERROR:", err);
});

process.on("unhandledRejection", (err) => {
    console.log("❌ PROMISE ERROR:", err);
});

const express = require("express");
const cors = require("cors");
const { supabase } = require("./supabase");
const { classifyEmergency } = require("./gemini");
const { sendAlertToRoles } = require("./notify");

const app = express();
app.use(cors());
app.use(express.json());

// ─── HEALTH CHECK ───────────────────────────────────────
app.get("/", (req, res) => {
    res.json({ status: "CrisisSync API is running ✅" });
});

// ─── REPORT AN EMERGENCY ─────────────────────────────────
app.post("/api/emergency", async (req, res) => {
    try {
        const { description, reported_by, location } = req.body;

        if (!description) {
            return res.status(400).json({ error: "Emergency description is required" });
        }

        console.log("🚨 New emergency reported:", description);

        // Step 1: Classify with Gemini AI
        console.log("🤖 Classifying with Gemini AI...");
        const classification = await classifyEmergency(description);
        console.log("✅ Classification:", classification);

        // Step 2: Save incident to Supabase
        const { data: incident, error: insertError } = await supabase
            .from("incidents")
            .insert({
                description,
                reported_by: reported_by || "Unknown",
                location: location || "Unknown",
                type: classification.type,
                severity: classification.severity,
                summary: classification.summary,
                sop_steps: classification.sop_steps,
                roles_notified: classification.roles_to_notify,
                status: "active",
            })
            .select()
            .single();

        if (insertError) throw insertError;

        console.log("💾 Incident saved with ID:", incident.id);

        // Step 3: Notify the right staff
        console.log("📢 Notifying roles:", classification.roles_to_notify);
        const notifyResult = await sendAlertToRoles(
            incident.id,
            classification.roles_to_notify,
            classification
        );

        // Step 4: Return result
        res.json({
            success: true,
            incident_id: incident.id,
            classification,
            notification_result: notifyResult,
            message: `Emergency classified as "${classification.type}" (${classification.severity}). ${notifyResult.notified} staff members alerted.`,
        });
    } catch (error) {
        console.error("❌ Error:", error);
        res.status(500).json({ error: "Something went wrong", details: error.message });
    }
});

// ─── GET ALL INCIDENTS ──────────────────────────────────
app.get("/api/incidents", async (req, res) => {
    try {
        const { data: incidents, error } = await supabase
            .from("incidents")
            .select("*")
            .order("timestamp", { ascending: false })
            .limit(20);

        if (error) throw error;

        res.json({ incidents });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ─── ADD STAFF MEMBER ───────────────────────────────────
app.post("/api/staff", async (req, res) => {
    try {
        const { name, role, phone } = req.body;
        const { data, error } = await supabase
            .from("staff")
            .insert({ name, role, phone })
            .select()
            .single();

        if (error) throw error;
        res.json({ success: true, staff: data });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// ─── RESOLVE AN INCIDENT ────────────────────────────────
app.patch("/api/incidents/:id/resolve", async (req, res) => {
    try {
        const { error } = await supabase
            .from("incidents")
            .update({ status: "resolved", resolved_at: new Date().toISOString() })
            .eq("id", req.params.id);

        if (error) throw error;
        res.json({ success: true, message: "Incident resolved" });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start server
const PORT = process.env.PORT || 3000;

app.listen(PORT, "0.0.0.0", () => {
    console.log(`🚀 CrisisSync server running on port ${PORT}`);
});