# reminder_logic.py

from datetime import datetime, timedelta
from supabase_client import supabase
import pytz  # For timezone support

def get_appointments_due():
    # Define timezone for Nairobi
    nairobi_tz = pytz.timezone("Africa/Nairobi")
    now = datetime.now(nairobi_tz)
    soon = now + timedelta(hours=24)

    print(f"🔍 Now (Nairobi): {now.isoformat()}")
    print(f"⏳ Soon (Nairobi +24h): {soon.isoformat()}")

    # ✅ Fetch only appointments that are:
    # - Not yet sent reminders
    # - Scheduled within the next 24 hours
    result = supabase.table("appointments") \
        .select("*") \
        .filter("reminder_sent", "eq", False) \
        .filter("appointment_at", "lt", soon.isoformat()) \
        .execute()

    if not result.data:
        print("📭 No upcoming appointments found.")
        return []

    print(f"🧾 Appointments due for reminder: {result.data}")
    return result.data
