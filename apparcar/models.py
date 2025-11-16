from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta


# USER MODEL (extends Django User)

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('owner', 'Owner'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return f"{self.username} ({self.role})"


# OWNER MODEL

class Owner(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="owner_profile")
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username


# PARKING MODEL

class Parking(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name="parkings")
    name = models.CharField("Nombre del estacionamiento", max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    car_spaces = models.PositiveIntegerField(default=0)
    moto_spaces = models.PositiveIntegerField(default=0)

    opening_time = models.TimeField()
    closing_time = models.TimeField()
    
    car_rate = models.DecimalField(max_digits=6, decimal_places=2)
    moto_rate = models.DecimalField(max_digits=6, decimal_places=2)
    nearby_place = models.CharField(max_length=100)  

    embedding = models.JSONField(null=True, blank=True, help_text="Embedding semántico (lista de floats)")

    
    def __str__(self):
        return f"{self.name} ({self.owner.user.username})"


# CAR MODEL

class Car(models.Model):
    VEHICLE_TYPE = [
        ('car', 'Car'),
        ('moto', 'Motorcycle'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="cars")
    license_plate = models.CharField(max_length=10, unique=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE, default='car')
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.license_plate} - {self.vehicle_type}"


# PARKING SESSION MODEL

class ParkingSession(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="sessions")
    parking = models.ForeignKey(Parking, on_delete=models.CASCADE, related_name="sessions")
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    paid = models.BooleanField(default=False)
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    def calculate_total(self):
        if not self.exit_time:
            return 0

        duration = self.exit_time - self.entry_time
        hours = duration.total_seconds() / 3600
        hours = max(1, round(hours))  # mínimo 1 hora

        if self.car.vehicle_type == 'car':
            rate = self.parking.car_rate
        else:
            rate = self.parking.moto_rate

        total = rate * hours
        return total

    def __str__(self):
        return f"{self.car.license_plate} en {self.parking.name}"

    class Meta:
        ordering = ["-entry_time"]
