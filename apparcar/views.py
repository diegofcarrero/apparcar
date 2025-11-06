# tuapp/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from django.contrib import messages
from .forms import ParkingForm
from .models import Parking, Owner


# --- Registro ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            if user.role == 'owner':
                return redirect('owner_dashboard')
            else:
                return redirect('user_dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


# --- Login ---
def login_view(request):
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                if user.role == 'owner':
                    return redirect('owner_dashboard')
                else:
                    return redirect('user_dashboard')
    else:
        form = CustomLoginForm()
    return render(request, 'login.html', {'form': form})


# --- Logout ---
def logout_view(request):
    logout(request)
    return redirect('login')


# --- Dashboards ---
@login_required
def user_dashboard(request):
    return render(request, 'user_dashboard.html')

@login_required
def owner_dashboard(request):
    return render(request, 'owner_dashboard.html')



# --- LISTAR PARQUEADEROS ---
@login_required
def owner_parkings(request):
    # Asegura que el Owner esté asociado al usuario actual
    owner, created = Owner.objects.get_or_create(user=request.user)
    
    # Filtra los parqueaderos que pertenecen a ese dueño
    parkings = Parking.objects.filter(owner=owner)
    
    context = {
        'parkings': parkings,
    }
    return render(request, 'owner/parking_list.html', context)

# --- CREAR PARQUEADERO ---
@login_required
def add_parking(request):
    owner = get_object_or_404(Owner, user=request.user)
    if request.method == 'POST':
        form = ParkingForm(request.POST)
        if form.is_valid():
            parking = form.save(commit=False)
            parking.owner = owner
            parking.save()
            messages.success(request, 'Parqueadero creado exitosamente.')
            return redirect('owner_parkings')
    else:
        form = ParkingForm()
    return render(request, 'owner/parking_form.html', {'form': form, 'title': 'Nuevo Parqueadero'})

# --- EDITAR PARQUEADERO ---
@login_required
def edit_parking(request, pk):
    owner = get_object_or_404(Owner, user=request.user)
    parking = get_object_or_404(Parking, pk=pk, owner=owner)
    if request.method == 'POST':
        form = ParkingForm(request.POST, instance=parking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parqueadero actualizado correctamente.')
            return redirect('owner_parkings')
    else:
        form = ParkingForm(instance=parking)
    return render(request, 'owner/parking_form.html', {'form': form, 'title': 'Editar Parqueadero'})

# --- ELIMINAR PARQUEADERO ---
@login_required
def delete_parking(request, pk):
    owner = get_object_or_404(Owner, user=request.user)
    parking = get_object_or_404(Parking, pk=pk, owner=owner)
    if request.method == 'POST':
        parking.delete()
        messages.success(request, 'Parqueadero eliminado.')
        return redirect('owner_parkings')
    return render(request, 'owner/parking_confirm_delete.html', {'parking': parking})


