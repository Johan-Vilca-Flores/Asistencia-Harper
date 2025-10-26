from twilio.rest import Client
from django.conf import settings
# ⚠️ Usa tus credenciales de Twilio Sandbox
ACCOUNT_SID = "AC3f84e3e3d38af1b8cbc06bcbf3ad9d12"
AUTH_TOKEN = "f0c5544677a96c890f8fc840c9dd3406"
FROM_WHATSAPP = "whatsapp:+14155238886"  # ← número de sandbox de Twilio


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
