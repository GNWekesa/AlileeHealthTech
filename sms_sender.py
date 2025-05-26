# This file is to send SMS reminders using Twilio.

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

twilio_client = Client(os.getenv("TWILIO_SID"), os.getenv("TWILIO_TOKEN"))

def send_reminder_sms(name, phone, appointment_time):
    message_body = f"Hi {name}, this is a reminder for your appointment on {appointment_time}."
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=os.getenv("TWILIO_PHONE"),
            to=phone
        )
        print(f"Reminder sent to {name} at {phone}: SID={message.sid}")
    except Exception as e:
        print(f"Error sending SMS to {phone}: {str(e)}")
