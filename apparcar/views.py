from django.http import HttpResponse

def login_view(request):
    return HttpResponse("Login page")

def register_view(request):
    return HttpResponse("Register page")

def user_dashboard(request):
    return HttpResponse("User Dashboard")

def owner_dashboard(request):
    return HttpResponse("Owner Dashboard")
