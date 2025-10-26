# attendance/utils.py
from twilio.rest import Client
from django.conf import settings

def send_whatsapp_message(to_number, body):
    """
    Envía un mensaje WhatsApp al número dado usando Twilio.
    """
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=f"whatsapp:{to_number}",
            body=body
        )
        print(f"✅ Mensaje enviado a {to_number}: SID={message.sid}")
        return message.sid
    except Exception as e:
        print(f"❌ Error enviando WhatsApp a {to_number}: {e}")
        return None

