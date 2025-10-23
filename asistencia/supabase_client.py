import os
from supabase import create_client
from django.conf import settings
# Leemos las variables de entorno (que deben existir en Vercel)
SUPABASE_URL =str(getattr(settings, "SUPABASE_URL", None))
SUPABASE_SERVICE_ROLE_KEY =str(getattr(settings, "SUPABASE_KEY", None))

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Faltan variables SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY")

# Creamos el cliente global
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
