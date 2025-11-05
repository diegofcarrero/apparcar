from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Owner, Parking, Car, ParkingSession


# CUSTOM USER ADMIN
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Rol del usuario', {'fields': ('role',)}),
    )


# OWNER ADMIN
@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone')
    search_fields = ('user__username',)


# PARKING ADMIN
@admin.register(Parking)
class ParkingAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'car_spaces', 'moto_spaces', 'car_rate', 'moto_rate', 'opening_time', 'closing_time')
    list_filter = ('owner',)
    search_fields = ('name', 'owner__user__username')


# CAR ADMIN

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'vehicle_type', 'brand', 'model', 'user')
    list_filter = ('vehicle_type',)
    search_fields = ('license_plate', 'user__username')


# PARKING SESSION ADMIN

@admin.register(ParkingSession)
class ParkingSessionAdmin(admin.ModelAdmin):
    list_display = ('car', 'parking', 'entry_time', 'exit_time', 'paid')
    list_filter = ('paid', 'parking')
    search_fields = ('car__license_plate',)
