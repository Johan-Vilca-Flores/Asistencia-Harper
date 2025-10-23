"""
URL configuration for mi_proyecto project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from asistencia.views import CheckInView, CheckOutView, AttendanceListView, UploadStudentPhotoView


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/attendances/check_in/", CheckInView.as_view(), name="attendance-check_in"),
    path("api/attendances/check_out/", CheckOutView.as_view(), name="attendance-check_out"),
    path("api/attendances/", AttendanceListView.as_view(), name="attendance-list"),
    path("api/attendances/upload_photo/", UploadStudentPhotoView.as_view(), name="upload-student-photo"),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

