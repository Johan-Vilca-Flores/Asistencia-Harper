# asistencia/models.py
from django.db import models
from django.utils import timezone

class Student(models.Model):
    dni = models.CharField(max_length=8, unique=True, verbose_name="DNI")
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    numero = models.CharField(max_length=15, null=True, blank=True, verbose_name="Teléfono")
    foto = models.ImageField(upload_to="students/", null=True, blank=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.dni})"

class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendances")
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)   # 👈 AÑADIDO
    date = models.DateField(default=timezone.localdate, editable=False)

    class Meta:
        ordering = ['-date', '-check_in']
        ##constraints = [
           ## models.UniqueConstraint(fields=["student", "date"], name="uniq_attendance_student_date")
       ##]

    def __str__(self):
        return f"Asistencia de {self.student} el {self.date}"


