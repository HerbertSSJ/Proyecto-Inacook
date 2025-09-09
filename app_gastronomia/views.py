from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .models import Platillo
from .forms import RegistroForm, PlatilloForm

def home(request):
    return redirect('platillos')

def register_view(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('platillos')
    else:
        form = RegistroForm()
    return render(request, "app_gastronomia/register.html", {"form": form})

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('platillos')
        else:
            return render(request, "app_gastronomia/login.html", {"error": "Usuario o contraseña incorrecta"})
    return render(request, "app_gastronomia/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def platillos_list(request):
    platillos = Platillo.objects.all()
    return render(request, "app_gastronomia/platillos_list.html", {"platillos": platillos})

@login_required
def platillo_detail(request, pk):
    platillo = get_object_or_404(Platillo, pk=pk)
    ingredientes = platillo.ingredientes.split(",") if platillo.ingredientes else []
    return render(request, "app_gastronomia/platillo_detail.html", {"platillo": platillo, "ingredientes": ingredientes})

@login_required
def agregar_platillo(request):
    if request.method == "POST":
        form = PlatilloForm(request.POST)
        if form.is_valid():
            platillo = form.save(commit=False)
            platillo.estudiante = request.user
            platillo.save()
            return redirect('platillos')
    else:
        form = PlatilloForm()
    return render(request, "app_gastronomia/agregar_platillo.html", {"form": form})

@login_required
def calculadora(request):
    total = None
    if request.method == "POST":
        precios = request.POST.getlist("precio")
        total = sum([float(p) for p in precios if p])
    return render(request, "app_gastronomia/calculadora.html", {"total": total})

@login_required
def perfil(request):
    return render(request, "app_gastronomia/perfil.html")
