from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Parking

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "password1", "password2", "role"]

class CustomLoginForm(AuthenticationForm):
    class Meta:
        model = CustomUser
        fields = ["username", "password"]

class ParkingForm(forms.ModelForm):
    class Meta:
        model = Parking
        fields = [
            "name",
            "latitude",
            "longitude",
            "car_spaces",
            "moto_spaces",
            "opening_time",
            "closing_time",
            "car_rate",
            "moto_rate",
            "nearby_place",
        ]
