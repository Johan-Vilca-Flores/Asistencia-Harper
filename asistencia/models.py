# asistencia/models.py
from django.db import models
from django.utils import timezone
from supabase import create_client
from django.conf import settings
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
class Student(models.Model):
    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero = models.CharField(max_length=15, null=True, blank=True, verbose_name="Teléfono")
    foto_url = models.URLField(null=True, blank=True, verbose_name="Foto (URL)")

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.dni})"
    def save(self, *args, **kwargs):
        # Si viene un archivo cargado temporalmente desde el admin
        uploaded_file = getattr(self, '_uploaded_file', None)
        if uploaded_file:
            # Nombre único por DNI
            file_path = f"students/{self.dni}.jpg"
            # Subida a Supabase Storage
            supabase.storage.from_("student-photos").upload(
                file_path,
                uploaded_file.read(),
                {"content-type": "image/jpeg"}
            )
            # Obtener URL pública
            public_url = supabase.storage.from_("student-photos").get_public_url(file_path)
            self.foto_url = public_url
        super().save(*args, **kwargs)

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)   # 👈 AÑADIDO
    date = models.DateField(default=timezone.localdate, editable=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "date"], name="uniq_attendance_student_date")
        ]

    def __str__(self):
        return f"Asistencia de {self.student} el {self.date}"
