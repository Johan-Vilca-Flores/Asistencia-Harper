
from django.shortcuts import render
from datetime import datetime
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.generics import ListAPIView
from .serializers import AttendanceSerializer
from .models import Student, Attendance
from .serializers import DniInputSerializer, AttendanceSerializer
from mi_proyecto.supabase_client import supabase
import uuid
from django.http import JsonResponse
from django.conf import settings
from supabase import create_client
SUPABASE_URL = str(settings.SUPABASE_URL)
SUPABASE_KEY = str(settings.SUPABASE_KEY)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# --- Permisos: ajusta a IsAuthenticated si ya tienes tokens y login ---
DEFAULT_PERMISSION = [permissions.AllowAny]  # cambia a [permissions.IsAuthenticated] en prod

class UploadStudentPhotoView(APIView):
    permission_classes = DEFAULT_PERMISSION

    def post(self, request, *args, **kwargs):
        dni = request.data.get("dni")
        photo = request.FILES.get("photo")

        if not dni:
            return Response({"detail": "Falta campo 'dni'."}, status=status.HTTP_400_BAD_REQUEST)
        if not photo:
            return Response({"detail": "Falta archivo 'photo'."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.get(dni=dni)
        except Student.DoesNotExist:
            return Response({"detail": "Alumno no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        bucket_name = "students"
        filename = f"{student.dni}/{uuid.uuid4().hex}_{photo.name}"

        try:
            # Leer archivo como bytes
            content = photo.read()

            # Subir directamente a Supabase
            upload_res = supabase.storage.from_(bucket_name).upload(filename, content)

            # Manejar posibles errores
            if isinstance(upload_res, dict) and upload_res.get("error"):
                return Response(
                    {"detail": "Error subiendo archivo", "error": upload_res["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            # Obtener URL pública (manejar tipo str o dict)
            public_data = supabase.storage.from_(bucket_name).get_public_url(filename)
            if isinstance(public_data, str):
                public_url = public_data
            else:
                public_url = (
                    public_data.get("publicUrl")
                    or public_data.get("public_url")
                    or public_data.get("url")
                )

            # Si no es público, generar una URL firmada
            if not public_url:
                signed = supabase.storage.from_(bucket_name).create_signed_url(filename, 60 * 60 * 24)
                public_url = signed.get("signedURL") or signed.get("signed_url")

            # Guardar la URL en el modelo del estudiante
            student.foto_url = public_url
            student.save(update_fields=["foto_url"])

            return Response(
                {
                    "message": "Foto subida correctamente.",
                    "foto_url": public_url,
                    "student": {
                        "dni": student.dni,
                        "nombres": student.nombres,
                        "apellidos": student.apellidos,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"detail": "Error interno al subir.", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

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
                qs = qs.filter(date=target_date)
            except ValueError:
                # Si viene mal la fecha, devuelve hoy (o podrías lanzar error 400)
                pass
                
        

        # Filtro opcional por DNI: ?dni=12345678
        dni = self.request.query_params.get("dni")
        if dni:
            qs = qs.filter(student__dni=dni)

        return qs
