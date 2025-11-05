from django.urls import path
from . import views

urlpatterns = [
    # Estas vistas las crearemos en el siguiente paso
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),
]
