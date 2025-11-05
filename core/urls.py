from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    # Redirección temporal al login (opcional)
    path('', lambda request: redirect('login/')),

    # Panel de administración
    path('admin/', admin.site.urls),

    # URLs de tu aplicación principal
    path('', include('apparcar.urls')),  # 👉 reemplaza 'tuapp' por el nombre real de tu app
]