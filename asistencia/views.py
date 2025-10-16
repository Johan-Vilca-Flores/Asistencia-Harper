from django.shortcuts import render
from datetime import datetime

from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from .serializers import AttendanceSerializer
from .models import Student, Attendance
from .serializers import DniInputSerializer, AttendanceSerializer

# --- Permisos: ajusta a IsAuthenticated si ya tienes tokens y login ---
DEFAULT_PERMISSION = [permissions.AllowAny]  # cambia a [permissions.IsAuthenticated] en prod

class CheckInView(APIView):
    permission_classes = DEFAULT_PERMISSION

    def post(self, request, *args, **kwargs):
        # Validamos el DNI recibido
        ser = DniInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data["dni"]

        # Buscamos el alumno
        try:
            student = Student.objects.get(dni=dni)
        except Student.DoesNotExist:
            return Response({"detail": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()

        # 🔹 Buscamos si ya existe un registro de asistencia ABIERTO (sin salida)
        open_attendance = Attendance.objects.filter(student=student, date=today, check_out__isnull=True).first()

        if open_attendance:
            # Si ya tiene un ingreso sin salida, no puede registrar otro hasta cerrar el anterior
            return Response({
                "message": "Ya tiene un ingreso sin registrar salida.",
                "attendance": AttendanceSerializer(open_attendance).data
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Si no tiene uno abierto, creamos uno nuevo con el check_in actual
        att = Attendance.objects.create(student=student, date=today, check_in=timezone.now())

        return Response({
            "message": "Ingreso registrado correctamente",
            "attendance": AttendanceSerializer(att).data
        }, status=status.HTTP_201_CREATED)


class CheckOutView(APIView):
    permission_classes = DEFAULT_PERMISSION

    def post(self, request, *args, **kwargs):
        # Validamos el DNI
        ser = DniInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data["dni"]

        # Buscamos el alumno
        try:
            student = Student.objects.get(dni=dni)
        except Student.DoesNotExist:
            return Response({"detail": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()

        # 🔹 Buscamos la última asistencia sin salida del día
        att = Attendance.objects.filter(student=student, date=today, check_out__isnull=True).order_by("-check_in").first()

        if not att:
            # Si no hay ingreso pendiente, no puede hacer salida
            return Response({
                "detail": "No hay un ingreso abierto para registrar salida."
            }, status=status.HTTP_400_BAD_REQUEST)

        # 🔹 Registramos la salida
        att.check_out = timezone.now()
        att.save(update_fields=["check_out"])

        return Response({
            "message": "Salida registrada correctamente",
            "attendance": AttendanceSerializer(att).data
        }, status=status.HTTP_200_OK)

        if att.check_out is None:
            att.check_out = timezone.now()
            att.save(update_fields=["check_out"])
            return Response({
                "message": "Salida registrada",
                "attendance": AttendanceSerializer(att).data
            }, status=status.HTTP_200_OK)
        else:
            # idempotente: ya tenía check_out
            return Response({
                "message": "La salida de hoy ya estaba registrada",
                "attendance": AttendanceSerializer(att).data
            }, status=status.HTTP_200_OK)

class AttendanceListView(ListAPIView):
    permission_classes = DEFAULT_PERMISSION
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        qs = (
            Attendance.objects
            .select_related("student")
            .order_by("-date", "-check_in")
        )
# Esto movi ojo 
       # Filtro opcional por fecha: ?date=YYYY-MM-DD
        date_str = self.request.query_params.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                qs = qs.filter(date=target_date)
            except ValueError:
                pass  # ignora formato inválido

        # Filtro opcional por DNI: ?dni=12345678
        dni = self.request.query_params.get("dni")
        if dni:
            qs = qs.filter(student__dni=dni)

        return qs



