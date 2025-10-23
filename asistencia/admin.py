from django import forms
from django.contrib import admin
from .models import Student, Attendance
from supabase import create_client
from django.conf import settings
import uuid
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
# Inicializar cliente Supabase
class StudentAdminForm(forms.ModelForm):
    subir_foto = forms.FileField(required=False, label="Subir foto")

    class Meta:
        model = Student
        fields = ['dni', 'nombres', 'apellidos', 'numero', 'foto_url']

    def save(self, commit=True):
        instance = super().save(commit=False)
        archivo = self.cleaned_data.get('subir_foto')

        if archivo:
            # Nombre del archivo = DNI.jpg dentro del bucket
            nombre_archivo = f"students/{instance.dni}.jpg"

            # Subir al bucket llamado 'students'
            supabase.storage.from_("students").upload(
                nombre_archivo,
                archivo.read(),
                {"content-type": "image/jpeg"}
            )

            # Obtener URL pública
            public_url = supabase.storage.from_("students").get_public_url(nombre_archivo)
            instance.foto_url = public_url

        if commit:
            instance.save()
        return instance


# --- Registro en el panel admin ---
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    form = StudentAdminForm
    list_display = ('dni', 'nombres', 'apellidos', 'foto_miniatura')
    readonly_fields = ('foto_url',)
    fields = ('dni', 'nombres', 'apellidos', 'numero', 'subir_foto', 'foto_url')

    def foto_miniatura(self, obj):
        if obj.foto_url:
            return f'<img src="{obj.foto_url}" width="80" height="80" style="border-radius:8px;">'
        return "Sin foto"
    foto_miniatura.allow_tags = True
    foto_miniatura.short_description = "Foto"
    
@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('id', 'student', 'date', 'check_in', 'check_out')
    list_filter = ('date',)
    search_fields = ('student__nombres', 'student__dni')
