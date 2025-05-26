# main.py

from reminder_logic import get_appointments_due
from whatsapp_sender import send_whatsapp_reminder
from supabase_client import supabase
import schedule
import time
import re  # For UUID cleanup

def reminder_job():
    print("🕒 Running reminder job...")
    appointments = get_appointments_due()

    if not appointments:
        print("✅ No pending appointments.")
        return

    for app in appointments:
        raw_patient_id = app['patient_id']
        
        # 🧼 Use regex to extract a valid UUID from messy patient_id
        match = re.search(
            r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}',
            str(raw_patient_id)
        )

        if not match:
            print(f"❌ Malformed patient_id: {raw_patient_id}")
            continue

        patient_id = match.group(0)
        print(f"🔎 Cleaned patient ID: {patient_id}")
        print(f"🔍 Querying patient with ID: {patient_id}")
        result = supabase.table("patients").select("*").eq("id", patient_id).execute()
        print(f"📦 Raw Supabase response: {result}")


        # ✅ Fetch patient details from Supabase
        result = supabase.table("patients").select("*").eq("id", patient_id).execute()

        if not result.data:
            print(f"⚠️ No patient found with ID {patient_id}")
            continue

        patient = result.data[0]  # Extract patient record

        print(f"📲 Sending WhatsApp to {patient['name']} at {patient['phone']}")
        send_whatsapp_reminder(patient['name'], patient['phone'], app['appointment_at'])

        # ✅ Mark reminder as sent
        supabase.table("appointments").update({"reminder_sent": True}).eq("id", app["id"]).execute()
        print(f"✅ Reminder marked as sent for appointment ID {app['id']}")

# Schedule to run every hour
schedule.every(1).hour.do(reminder_job)

# Optional: Run it immediately at startup
reminder_job()

# Keep running
while True:
    schedule.run_pending()
    time.sleep(60)
