require("dotenv").config();
const { db, admin } = require("./supabase");

const staff = [
    { name: "Dr. Priya Sharma", role: "medical_team", phone: "+91-9000000001" },
    { name: "Rajan Verma", role: "security", phone: "+91-9000000002" },
    { name: "Amit Nair", role: "maintenance", phone: "+91-9000000003" },
    { name: "Sunita Kapoor", role: "manager", phone: "+91-9000000004" },
    { name: "Chef Ramesh", role: "kitchen_staff", phone: "+91-9000000005" },
];

async function seed() {
    for (const member of staff) {
        const ref = await db.collection("staff").add({
            ...member,
            fcm_token: null,
            created_at: admin.firestore.FieldValue.serverTimestamp(),
        });
        console.log(`✅ Added: ${member.name} (${member.role}) → ID: ${ref.id}`);
    }
    console.log("🎉 Done seeding staff!");
    process.exit(0);
}

seed();