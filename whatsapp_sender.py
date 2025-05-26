import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

def send_whatsapp_reminder(name, phone, appointment_time):
    message_body = f"👋 Hi {name}, this is a reminder for your clinic appointment on {appointment_time}.\n\nReply with 'CONFIRM' or 'RESCHEDULE' to update your status."
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_='whatsapp:+14155238886',  # Twilio Sandbox Number
            to=f'whatsapp:{+254785687846}'
        )
        print(f"✅ WhatsApp reminder sent to {name} at {+254785687846}: SID={message.sid}")
    except Exception as e:
        print(f"❌ Error sending WhatsApp to {+254785687846}: {str(e)}")
