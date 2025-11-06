from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/user/', views.user_dashboard, name='user_dashboard'),
    path('dashboard/owner/', views.owner_dashboard, name='owner_dashboard'),

    # CRUD Parqueaderos
    path('owner/parkings/', views.owner_parkings, name='owner_parkings'),
    path('owner/parkings/add/', views.add_parking, name='add_parking'),
    path('owner/parkings/<int:pk>/edit/', views.edit_parking, name='edit_parking'),
    path('owner/parkings/<int:pk>/delete/', views.delete_parking, name='delete_parking'),


]