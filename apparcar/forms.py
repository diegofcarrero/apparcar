from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser
from .models import Parking

class BootstrapFormMixin:
    """Agrega la clase form-control de Bootstrap a los campos."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

class CustomUserCreationForm(BootstrapFormMixin, UserCreationForm):
    ROLE_CHOICES = [
        ('user', 'Usuario'),
        ('owner', 'Dueño de Parqueadero'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label="Tipo de usuario")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'password1', 'password2')


class CustomLoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Usuario")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")



class ParkingForm(forms.ModelForm):
    class Meta:
        model = Parking
        exclude = ['owner']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_spaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'moto_spaces': forms.NumberInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'car_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'moto_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'nearby_place': forms.TextInput(attrs={'class': 'form-control'}),
        }
