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
        ser = DniInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data["dni"]

        try:
            student = Student.objects.get(dni=dni)
        except Student.DoesNotExist:
            return Response({"detail": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        att, created = Attendance.objects.get_or_create(student=student, date=today, defaults={"check_in": timezone.now()})

        if att.check_in is None:
            att.check_in = timezone.now()
            att.save(update_fields=["check_in"])
            return Response({
                "message": "Ingreso registrado",
                "created": created,
                "attendance": AttendanceSerializer(att).data
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        else:
            # idempotente: ya tenía check_in
            return Response({
                "message": "El ingreso de hoy ya estaba registrado",
                "attendance": AttendanceSerializer(att).data
            }, status=status.HTTP_200_OK)


class CheckOutView(APIView):
    permission_classes = DEFAULT_PERMISSION

    def post(self, request, *args, **kwargs):
        ser = DniInputSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dni = ser.validated_data["dni"]

        try:
            student = Student.objects.get(dni=dni)
        except Student.DoesNotExist:
            return Response({"detail": "Alumno no encontrado"}, status=status.HTTP_404_NOT_FOUND)

        today = timezone.localdate()
        try:
            att = Attendance.objects.get(student=student, date=today)
        except Attendance.DoesNotExist:
            # Si no hay check-in previo, puedes crear el registro y marcar solo la salida
            # o devolver error. Aquí devolvemos error para forzar flujo correcto:
            return Response(
                {"detail": "No existe asistencia de hoy para este alumno (primero haga check-in)."},
                status=status.HTTP_400_BAD_REQUEST
            )

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

        # ?date=YYYY-MM-DD  (por defecto: hoy)
        date_str = self.request.query_params.get("date")
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                # Si viene mal la fecha, devuelve hoy (o podrías lanzar error 400)
                target_date = timezone.localdate()
        else:
            target_date = timezone.localdate()
        qs = qs.filter(date=target_date)

        # Filtro opcional por DNI: ?dni=12345678
        dni = self.request.query_params.get("dni")
        if dni:
            qs = qs.filter(student__dni=dni)

        return qs

