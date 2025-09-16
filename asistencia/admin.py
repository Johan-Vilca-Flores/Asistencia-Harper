from django.contrib import admin
from .models import Student, Attendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("dni", "nombres", "apellidos")
    search_fields = ("dni", "nombres", "apellidos")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("student", "date", "check_in", "check_out")  # ✅ ahora existe
    list_filter = ("date",)
    search_fields = ("student__dni", "student__nombres", "student__apellidos")
    ordering = ("-date", "-check_in")
