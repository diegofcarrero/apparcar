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
    path('user/parking/<int:parking_id>/', views.parking_detail, name='parking_detail'),


    path('owner/parking/<int:parking_id>/sessions/', views.parking_sessions, name='parking_sessions'),
    path('owner/parking/<int:parking_id>/sessions/', views.parking_sessions, name='parking_sessions'),
    path('owner/parking/<int:parking_id>/sessions/add/', views.add_parking_session, name='add_parking_session'),
    path('owner/session/<int:session_id>/close/', views.close_parking_session, name='close_parking_session'),
    path('owner/session/<int:session_id>/close/', views.close_parking_session, name='close_parking_session'),


    # --- USER ROUTES ---
    path("user/dashboard/", views.user_dashboard, name="user_dashboard"),
    path("user/vehicles/", views.vehicle_list, name="vehicle_list"),
    path("user/vehicles/add/", views.add_vehicle, name="add_vehicle"),
    path("user/vehicles/<int:vehicle_id>/edit/", views.edit_vehicle, name="edit_vehicle"),
    path("user/vehicles/<int:vehicle_id>/delete/", views.delete_vehicle, name="delete_vehicle"),

    path('user/parkings/', views.parking_list_user, name='parking_list_user'),

    path("user/parking/<int:parking_id>/start/", views.start_parking_session, name="start_parking_session"),
    path("user/session/<int:session_id>/close/", views.close_user_session, name="close_user_session"),
    
    path('user/session/<int:session_id>/total/', views.session_total_ajax, name='session_total_ajax'),

    


]