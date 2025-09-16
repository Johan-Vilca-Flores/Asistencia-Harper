from rest_framework import serializers
from .models import Student, Attendance

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "dni", "nombres", "apellidos", "numero", "foto"]

class AttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)

    class Meta:
        model = Attendance
        fields = ["id", "student", "date", "check_in", "check_out"]

# Serializer auxiliar para recibir DNI en check-in/check-out
class DniInputSerializer(serializers.Serializer):
    dni = serializers.CharField(max_length=8)
