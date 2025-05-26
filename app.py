from flask import Flask, render_template, request, redirect
from datetime import datetime
from supabase import create_client
from twilio.rest import Client as TwilioClient
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Setup Flask
app = Flask(__name__)

# Setup Supabase
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# Setup Twilio
twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_WHATSAPP_FROM")


twilio = TwilioClient(twilio_sid, twilio_token)

### ROUTES ###

@app.route('/')
@app.route('/add')
def add_appointment():
    try:
        response = supabase.table("patients").select("id, name, phone").execute()
        patients = response.data
        print(f"✅ Patients fetched from Supabase: {patients}")
        return render_template("add_appointment.html", patients=patients)
    except Exception as e:
        print(f"❌ Error fetching patients: {e}")
        return f"❌ Error fetching patients: {e}"

@app.route('/submit', methods=['POST'])
def submit():
    patient_id = request.form['patient_id']
    appointment_at = request.form['appointment_at']
    print(f"📥 Received form data: {patient_id} {appointment_at}")

    # Save appointment
    try:
        result = supabase.table("appointments").insert({
            "patient_id": patient_id,
            "appointment_at": appointment_at,
            "reminder_sent": False
        }).execute()
        print(f"✅ Appointment inserted: {result.data}")
    except Exception as e:
        print(f"❌ Error saving appointment: {e}")
        return f"❌ Error saving appointment: {e}"

    # Fetch patient info
    try:
        patient_result = supabase.table("patients").select("name, phone").eq("id", patient_id).single().execute()
        patient = patient_result.data
        print(f"👤 Patient info: {patient}")
    except Exception as e:
        print(f"❌ Error fetching patient info: {e}")
        return f"❌ Error fetching patient info: {e}"

    # Send WhatsApp reminder
    try:
        message = f"Hello {patient['name']}, this is a reminder for your appointment at {appointment_at} UTC."
        sent_msg = twilio.messages.create(
            body=message,
            from_=TWILIO_FROM,
            to=f"whatsapp:{patient['phone']}"
        )
        print("📨 Twilio message SID:", sent_msg.sid)

        # Update reminder_sent
        supabase.table("appointments").update({"reminder_sent": True}) \
            .eq("patient_id", patient_id).eq("appointment_at", appointment_at).execute()

    except Exception as e:
        print(f"❌ Error sending WhatsApp: {e}")
        return f"❌ Error sending WhatsApp: {e}"

    return redirect('/success')

@app.route('/success')
def success():
    return "✅ Appointment saved and WhatsApp reminder sent!"

@app.route('/upcoming')
def view_upcoming():
    try:
        response = supabase.rpc("get_upcoming_appointments").execute()
        upcoming = response.data
        return render_template("upcoming.html", appointments=upcoming)
    except Exception as e:
        print(f"❌ Error loading upcoming appointments: {e}")
        return f"❌ Error loading upcoming appointments: {e}"

@app.route('/send_reminders')
def send_reminders():
    try:
        # Get future appointments that haven't been reminded
        res = supabase.table("appointments").select("id, patient_id, appointment_at") \
            .eq("reminder_sent", False).gt("appointment_at", datetime.utcnow().isoformat()).execute()

        appointments = res.data
        print(f"🔔 Appointments to remind: {appointments}")

        for appt in appointments:
            # Get patient
            patient_res = supabase.table("patients").select("name, phone").eq("id", appt["patient_id"]).single().execute()
            patient = patient_res.data

            # Send message
            message = f"Hi {patient['name']}, this is your reminder for your appointment at {appt['appointment_at']} UTC."
            sent_msg = twilio.messages.create(
                body=message,
                from_=TWILIO_FROM,
                to=f"whatsapp:{patient['phone']}"
            )
            print(f"📨 Sent reminder SID: {sent_msg.sid} for appointment {appt['id']}")

            # Update reminder_sent
            supabase.table("appointments").update({"reminder_sent": True}) \
                .eq("id", appt["id"]).execute()

        return "✅ All reminders sent."
    except Exception as e:
        print(f"❌ Error sending batch reminders: {e}")
        return f"❌ Error sending batch reminders: {e}"


if __name__ == '__main__':
    app.run(debug=True)
