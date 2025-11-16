
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, CustomLoginForm
from .models import CustomUser
from django.contrib import messages
from .forms import ParkingForm
from .models import Parking, Owner, ParkingSession, Car
from django.utils import timezone
from django.http import JsonResponse
import json
from .semantic_search import semantic_search
from django.db import models


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


@login_required
def parking_sessions(request, parking_id):
    parking = get_object_or_404(Parking, id=parking_id, owner__user=request.user)
    sessions = ParkingSession.objects.filter(parking=parking).select_related('car')

    return render(request, 'owner/parking_sessions.html', {
        'parking': parking,
        'sessions': sessions
    })



@login_required
def add_parking_session(request, parking_id):
    owner = get_object_or_404(Owner, user=request.user)
    parking = get_object_or_404(Parking, id=parking_id, owner=owner)

    if request.method == 'POST':
        license_plate = request.POST.get('license_plate')
        try:
            car = Car.objects.get(license_plate=license_plate)
        except Car.DoesNotExist:
            messages.error(request, "No existe un vehículo con esa placa.")
            return redirect('parking_sessions', parking_id=parking_id)

        # Crear nueva sesión si no hay una activa para ese carro
        existing = ParkingSession.objects.filter(car=car, parking=parking, exit_time__isnull=True)
        if existing.exists():
            messages.warning(request, "Este vehículo ya tiene una sesión activa en este parqueadero.")
        else:
            ParkingSession.objects.create(car=car, parking=parking)
            messages.success(request, "Entrada registrada correctamente.")

        return redirect('parking_sessions', parking_id=parking_id)

    return render(request, 'owner/add_parking_session.html', {'parking': parking})

@login_required
def close_parking_session(request, session_id):
    """Finaliza una sesión de parqueo, calcula el total y marca como pagada."""
    session = get_object_or_404(ParkingSession, id=session_id)

    if not session.exit_time:
        session.exit_time = timezone.now()
        session.total_amount = session.calculate_total()  # 👈 Aquí el cálculo automático
        session.paid = True  # Puedes dejar False si planeas manejar pagos aparte
        session.save()
        messages.success(request, f"✅ Sesión finalizada. Total a pagar: ${session.total_amount:.2f}")
    else:
        messages.warning(request, "⚠️ Esta sesión ya fue finalizada anteriormente.")

    return redirect('parking_sessions', parking_id=session.parking.id)


# ---------- USER VEHICLES MANAGEMENT ----------
@login_required
def user_dashboard(request):
    """Panel principal del usuario con lista de vehículos y sesiones activas."""
    if request.user.role != "user":
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect("login")

    vehicles = Car.objects.filter(user=request.user)
    active_sessions = ParkingSession.objects.filter(car__user=request.user, exit_time__isnull=True).select_related("car", "parking")

    return render(request, "user/dashboard.html", {
        "vehicles": vehicles,
        "active_sessions": active_sessions,
    })



@login_required
def vehicle_list(request):
    """Lista de vehículos del usuario"""
    if request.user.role != "user":
        return redirect("home")

    vehicles = Car.objects.filter(user=request.user)
    return render(request, "user/vehicle_list.html", {"vehicles": vehicles})


@login_required
def add_vehicle(request):
    """Registrar un nuevo vehículo"""
    if request.user.role != "user":
        return redirect("home")

    if request.method == "POST":
        license_plate = request.POST.get("license_plate").upper()
        vehicle_type = request.POST.get("vehicle_type")
        brand = request.POST.get("brand")
        model = request.POST.get("model")
        color = request.POST.get("color")

        if Car.objects.filter(license_plate=license_plate).exists():
            messages.warning(request, "Ya existe un vehículo con esa placa.")
            return redirect("vehicle_list")

        Car.objects.create(
            user=request.user,
            license_plate=license_plate,
            vehicle_type=vehicle_type,
            brand=brand,
            model=model,
            color=color
        )
        messages.success(request, "Vehículo registrado correctamente.")
        return redirect("vehicle_list")

    return render(request, "user/add_vehicle.html")


@login_required
def edit_vehicle(request, vehicle_id):
    """Editar vehículo"""
    vehicle = get_object_or_404(Car, id=vehicle_id, user=request.user)

    if request.method == "POST":
        vehicle.license_plate = request.POST.get("license_plate").upper()
        vehicle.vehicle_type = request.POST.get("vehicle_type")
        vehicle.brand = request.POST.get("brand")
        vehicle.model = request.POST.get("model")
        vehicle.color = request.POST.get("color")
        vehicle.save()
        messages.success(request, "Vehículo actualizado.")
        return redirect("vehicle_list")

    return render(request, "user/edit_vehicle.html", {"vehicle": vehicle})


@login_required
def delete_vehicle(request, vehicle_id):
    """Eliminar vehículo"""
    vehicle = get_object_or_404(Car, id=vehicle_id, user=request.user)
    vehicle.delete()
    messages.success(request, "Vehículo eliminado.")
    return redirect("vehicle_list")

# --- LISTADO DE PARQUEADEROS PARA USUARIOS ---
from django.db.models import Q

from django.db.models import Q
from django.contrib import messages

@login_required
def parking_list_user(request):
    query = request.GET.get("q", "")
    vehicle_id = request.GET.get("vehicle_id")

    selected_vehicle = None

    # Obtener vehículo seleccionado SI existe
    if vehicle_id:
        selected_vehicle = get_object_or_404(Car, id=vehicle_id, user=request.user)

    # Filtrar parqueaderos
    parkings = Parking.objects.all()

    if query:
        parkings = parkings.filter(
            models.Q(name__icontains=query) |
            models.Q(nearby_place__icontains=query)
        )

    # Convertir parqueaderos a JSON para Google Maps
    parkings_json = json.dumps([
        {
            "id": p.id,
            "name": p.name,
            "latitude": float(p.latitude),
            "longitude": float(p.longitude),
            "car_spaces": p.car_spaces,
            "moto_spaces": p.moto_spaces,
            "opening_time": p.opening_time.strftime("%H:%M") if p.opening_time else "",
            "closing_time": p.closing_time.strftime("%H:%M") if p.closing_time else "",
        }
        for p in parkings
    ])

    return render(request, "user/parking_list_user.html", {
        "parkings": parkings,
        "query": query,
        "parkings_json": parkings_json,
        "selected_vehicle": selected_vehicle,
    })


def parking_detail(request, parking_id):
    parking = get_object_or_404(Parking, id=parking_id)
    return render(request, 'user/parking_detail.html', {'parking': parking})


@login_required
def start_parking_session(request, parking_id):
    """Crea una sesión de parqueo para el vehículo seleccionado."""
    if request.user.role != "user":
        messages.error(request, "Solo los usuarios pueden iniciar sesiones de parqueo.")
        return redirect("login")

    vehicle_id = request.GET.get("vehicle_id")
    if not vehicle_id:
        messages.warning(request, "Debes seleccionar un vehículo antes de estacionar.")
        return redirect("parking_list_user")

    try:
        vehicle = Car.objects.get(id=vehicle_id, user=request.user)
    except Car.DoesNotExist:
        messages.error(request, "El vehículo seleccionado no es válido.")
        return redirect("parking_list_user")

    parking = get_object_or_404(Parking, id=parking_id)

    # Evita duplicar sesiones activas para el mismo vehículo
    existing = ParkingSession.objects.filter(car=vehicle, exit_time__isnull=True)
    if existing.exists():
        messages.warning(request, "Este vehículo ya tiene una sesión activa.")
        return redirect("parking_list_user")

    # Crear sesión nueva
    ParkingSession.objects.create(car=vehicle, parking=parking)
    messages.success(request, f"🚗 Has estacionado en '{parking.name}' correctamente.")

    return redirect("user_dashboard")

@login_required
def close_user_session(request, session_id):
    """Permite al usuario finalizar su sesión de parqueo."""
    session = get_object_or_404(ParkingSession, id=session_id, car__user=request.user)

    if session.exit_time:
        messages.warning(request, "Esta sesión ya fue finalizada.")
        return redirect("user_dashboard")

    session.exit_time = timezone.now()
    session.total_amount = session.calculate_total()
    session.paid = True
    session.save()

    messages.success(request, f"✅ Sesión finalizada. Total a pagar: ${session.total_amount:.2f}")
    return redirect("user_dashboard")



@login_required
def session_total_ajax(request, session_id):
    session = get_object_or_404(ParkingSession, id=session_id)
    total = session.calculate_total()
    return JsonResponse({'total': float(total)})

@login_required
def user_semantic_search(request):
    query = request.GET.get('q', '').strip()
    results = []
    scores = []
    if query:
        hits = semantic_search(query, top_k=20)  # [(parking, score), ...]
        # puedes aplicar filtros adicionales (p. ej. parking abierto ahora)
        for parking, score in hits:
            results.append(parking)
            scores.append(score)

    return render(request, 'user/semantic_search.html', {
        'query': query,
        'results': results,
        'scores': scores,
    })

