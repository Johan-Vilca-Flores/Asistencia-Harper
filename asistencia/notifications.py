from twilio.rest import Client
from django.conf import settings
import os
from twilio.rest import Client
client = Client(
    os.environ.get("TWILIO_ACCOUNT_SID"),
    os.environ.get("TWILIO_AUTH_TOKEN")
)

def send_whatsapp_message(to_number, body):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=settings.TWILIO_WHATSAPP_FROM,
        body=body,
        to=f"whatsapp:{to_number}" if not to_number.startswith("whatsapp:") else to_number
    )


def build_attendance_message(nombre, dni, check_in=None, check_out=None):
    msg = f"📚 Registro de asistencia\n👤 Alumno: {nombre} ({dni})\n"
    if check_in:
        msg += f"🕒 Ingreso: {check_in.strftime('%H:%M:%S')}\n"
    if check_out:
        msg += f"🚪 Salida: {check_out.strftime('%H:%M:%S')}\n"
    return msg
