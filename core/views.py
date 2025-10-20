from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth import authenticate, login, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from decimal import Decimal
import json

from .models import (
    Usuario, Rol, Historial, Comprobante, RecetaIngrediente,
    Receta, Ingrediente, UnidadMedicion
)
from .forms import RecetaForm, IngredienteForm, UnidadMedicionForm

Usuario = get_user_model()


# -------------------- LOGIN --------------------
def home(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        contraseña = request.POST.get("contraseña")

        user = authenticate(request, username=nombre, password=contraseña)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
            return redirect('home')

    return render(request, 'login.html')


# -------------------- REGISTRO --------------------
def register(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        rol_id = request.POST.get("rol")

        if not nombre or not correo or not contraseña or not rol_id:
            messages.error(request, "Todos los campos son obligatorios")
            return redirect('register')

        if Usuario.objects.filter(username=nombre).exists():
            messages.error(request, "Nombre de usuario ya existe")
            return redirect('register')
        if Usuario.objects.filter(email=correo).exists():
            messages.error(request, "Correo ya registrado")
            return redirect('register')

        try:
            rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            messages.error(request, "Rol seleccionado no existe")
            return redirect('register')

        user = Usuario.objects.create_user(
            username=nombre,
            email=correo,
            password=contraseña,
            rol=rol.NombreRol
        )

        messages.success(request, "Usuario creado exitosamente")
        return redirect('home')

    roles = Rol.objects.all()
    return render(request, 'register.html', {'roles': roles})


# -------------------- DASHBOARD --------------------
@login_required
def dashboard(request):
    usuario = request.user
    return render(request, "dashboard.html", {
        "nombre": usuario.username,
        "rol": usuario.rol
    })


# -------------------- SUBIR RECETA --------------------
@login_required
def subir_receta(request):
    ingredientes = Ingrediente.objects.all()
    unidades = UnidadMedicion.objects.all()

    if request.method == "POST":
        receta_form = RecetaForm(request.POST, request.FILES)

        if receta_form.is_valid():
            receta = receta_form.save()

            # Parsear el JSON con los ingredientes seleccionados
            ingredientes_json = request.POST.get('ingredientes_json', '[]')
            try:
                ingredientes_data = json.loads(ingredientes_json)
            except json.JSONDecodeError:
                ingredientes_data = []

            costo_total = Decimal(0)

            # Procesar cada ingrediente del formulario
            for ing in ingredientes_data:
                if not ing.get('id') or not ing.get('cantidad'):
                    continue

                try:
                    ingrediente = Ingrediente.objects.get(idIngrediente=int(ing['id']))
                except Ingrediente.DoesNotExist:
                    continue

                cantidad = Decimal(ing['cantidad'])
                precio_unitario = Decimal(ing.get('precio', 0))
                unidad = ing.get('unidad', '')  # 🔹 Captura la unidad elegida

                # Crear la relación RecetaIngrediente
                RecetaIngrediente.objects.create(
                    Receta_idReceta=receta.Nombre_Receta,
                    Ingrediente_idIngrediente=ingrediente.Nombre_Ingrediente,
                    Cantidad=cantidad,
                )

                costo_total += precio_unitario * cantidad

            # Calcular totales
            factor_multiplicacion = Decimal(1.3)
            iva = Decimal(0.19)
            precio_bruto = costo_total * factor_multiplicacion * (1 + iva)

            # Crear comprobante
            Comprobante.objects.create(
                Receta=receta.Nombre_Receta,
                Costo_Total=int(costo_total),
                Factor_Multiplicacion=factor_multiplicacion,
                Iva=iva,
                Precio_Bruto=int(precio_bruto)
            )

            # Registrar en el historial
            Historial.objects.create(
                Usuario=str(request.user),
                Receta=receta.Nombre_Receta,
                Cambio_Realizado=f"Receta '{receta.Nombre_Receta}' creada con éxito."
            )

            messages.success(request, "Receta subida exitosamente.")
            return redirect("ver_recetas")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        receta_form = RecetaForm()

    return render(request, "subir_receta.html", {
        "receta_form": receta_form,
        "ingredientes": ingredientes,
        "unidades": unidades,
    })


# -------------------- VER RECETAS --------------------
@login_required
def ver_recetas(request):
    usuario = str(request.user)
    recetas_nombres = Historial.objects.filter(Usuario=usuario).values_list('Receta', flat=True).distinct()
    recetas = Receta.objects.filter(Nombre_Receta__in=recetas_nombres)

    recetas_data = []
    for receta in recetas:
        ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta)
        ingredientes_info = []

        for ri in ingredientes:
            try:
                ingrediente = Ingrediente.objects.get(Nombre_Ingrediente=ri.Ingrediente_idIngrediente)
                unidad = ingrediente.UnidadMedicion_idUnidadMedicion
                unidad_obj = None

                if str(unidad).isdigit():
                    unidad_obj = UnidadMedicion.objects.filter(idUnidadMedicion=int(unidad)).first()

                unidad_texto = (
                    f"{unidad_obj.Nombre_Unidad} ({unidad_obj.Abreviatura})"
                    if unidad_obj else str(unidad)
                )

                ingredientes_info.append({
                    "Cantidad": ri.Cantidad,
                    "Nombre": ingrediente.Nombre_Ingrediente,
                    "Unidad": unidad_texto,
                    "Precio": ingrediente.Costo_Unitario,
                    "Calidad": ingrediente.Calidad
                })
            except Ingrediente.DoesNotExist:
                ingredientes_info.append({
                    "Cantidad": ri.Cantidad,
                    "Nombre": ri.Ingrediente_idIngrediente,
                    "Unidad": "—",
                    "Precio": 0,
                    "Calidad": "Desconocida"
                })

        comprobante = Comprobante.objects.filter(Receta=receta.Nombre_Receta).first()
        precio = comprobante.Precio_Bruto if comprobante else "No calculado"

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes_info,
            "precio": precio
        })

    ingredientes_global = Ingrediente.objects.select_related("UnidadMedicion_idUnidadMedicion").all()

    return render(request, "ver_recetas.html", {
        "recetas_data": recetas_data,
        "ingredientes_global": ingredientes_global
    })


# -------------------- COMPROBANTE --------------------
@login_required
def comprobante_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)
    comprobante = Comprobante.objects.filter(Receta=receta.Nombre_Receta).first()
    ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta)

    subtotal = 0
    ingredientes_info = []

    for ri in ingredientes:
        try:
            ingrediente = Ingrediente.objects.get(Nombre_Ingrediente=ri.Ingrediente_idIngrediente)
            unidad = ingrediente.UnidadMedicion_idUnidadMedicion
            unidad_obj = None

            if str(unidad).isdigit():
                unidad_obj = UnidadMedicion.objects.filter(idUnidadMedicion=int(unidad)).first()

            unidad_texto = (
                f"{unidad_obj.Nombre_Unidad} ({unidad_obj.Abreviatura})"
                if unidad_obj else str(unidad)
            )

            subtotal += float(ri.Cantidad) * float(ingrediente.Costo_Unitario)
            ingredientes_info.append({
                "nombre": ingrediente.Nombre_Ingrediente,
                "cantidad": ri.Cantidad,
                "unidad": unidad_texto,
                "precio": ingrediente.Costo_Unitario,
                "calidad": ingrediente.Calidad
            })
        except Ingrediente.DoesNotExist:
            ingredientes_info.append({
                "nombre": ri.Ingrediente_idIngrediente,
                "cantidad": ri.Cantidad,
                "unidad": "—",
                "precio": 0,
                "calidad": "Desconocida"
            })

    return render(request, "comprobante_receta.html", {
        "receta": receta,
        "comprobante": comprobante,
        "ingredientes": ingredientes_info,
        "subtotal": subtotal
    })


# -------------------- PERFIL --------------------
@login_required
def perfil_view(request):
    usuario = request.user
    if request.method == "POST":
        usuario.username = request.POST.get("username")
        usuario.email = request.POST.get("email")
        usuario.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('perfil')

    return render(request, 'perfil.html', {'usuario': usuario, 'rol': usuario.rol})


# -------------------- HISTORIAL --------------------
@login_required
def ver_historial(request):
    historial = Historial.objects.all().order_by('-Fecha_Modificacion')
    return render(request, 'ver_historial.html', {'historial': historial})


# -------------------- CAMBIAR CONTRASEÑA --------------------
class CambiarContraseñaView(PasswordChangeView):
    template_name = 'cambiar_contraseña.html'
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña se cambió correctamente.")
        return super().form_valid(form)


# -------------------- FUNCIONES AUXILIARES --------------------
def solo_profesor(user):
    return user.is_authenticated and user.rol.lower() == "profesor"


@login_required
def crear_ingrediente(request):
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    if request.method == "POST":
        form = IngredienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ingrediente creado exitosamente.")
            return redirect("dashboard")
    else:
        form = IngredienteForm()

    return render(request, "crear_ingrediente.html", {"form": form})


@login_required
def ver_ingredientes(request):
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para ver los ingredientes.")

    ingredientes = Ingrediente.objects.all()
    unidades = {u.idUnidadMedicion: u for u in UnidadMedicion.objects.all()}

    for ing in ingredientes:
        id_unidad = ing.UnidadMedicion_idUnidadMedicion
        if str(id_unidad).isdigit() and int(id_unidad) in unidades:
            unidad_obj = unidades[int(id_unidad)]
            ing.unidad_nombre = f"{unidad_obj.Nombre_Unidad} ({unidad_obj.Abreviatura})"
        else:
            ing.unidad_nombre = id_unidad

    return render(request, "ver_ingredientes.html", {"ingredientes": ingredientes})

@login_required
def ver_recetas_alumnos(request):
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    recetas = Receta.objects.all()
    recetas_data = []

    for receta in recetas:
        ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta)
        comprobante = Comprobante.objects.filter(Receta=receta.Nombre_Receta).first()
        precio = comprobante.Precio_Bruto if comprobante else "No calculado"

        historial = Historial.objects.filter(Receta=receta.Nombre_Receta).first()
        usuario_texto = historial.Usuario if historial else "Desconocido"

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes,
            "precio": precio,
            "usuario": usuario_texto
        })

    ingredientes_global = Ingrediente.objects.select_related("UnidadMedicion_idUnidadMedicion").all()

    return render(request, "ver_recetas_alumnos.html", {
        "recetas_data": recetas_data,
        "ingredientes_global": ingredientes_global
    })

@login_required
def editar_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)
    ingredientes = Ingrediente.objects.all()
    unidades = UnidadMedicion.objects.all()

    # Obtener ingredientes existentes
    receta_ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta)

    if request.method == "POST":
        receta_form = RecetaForm(request.POST, request.FILES, instance=receta)
        if receta_form.is_valid():
            receta_form.save()

            # Borrar ingredientes previos y volver a guardar
            RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta).delete()

            ingredientes_json = request.POST.get('ingredientes_json', '[]')
            try:
                ingredientes_data = json.loads(ingredientes_json)
            except json.JSONDecodeError:
                ingredientes_data = []

            for ing in ingredientes_data:
                if not ing.get('id') or not ing.get('cantidad'):
                    continue
                ingrediente = Ingrediente.objects.get(idIngrediente=int(ing['id']))
                cantidad = Decimal(ing['cantidad'])

                RecetaIngrediente.objects.create(
                    Receta_idReceta=receta.Nombre_Receta,
                    Ingrediente_idIngrediente=ingrediente.Nombre_Ingrediente,
                    Cantidad=cantidad
                )

            messages.success(request, "Receta actualizada correctamente.")
            return redirect('ver_recetas')
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        receta_form = RecetaForm(instance=receta)

    return render(request, "editar_receta.html", {
        "receta_form": receta_form,
        "receta": receta,
        "ingredientes": ingredientes,
        "unidades": unidades,
        "receta_ingredientes": receta_ingredientes
    })

@login_required
def borrar_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)
    receta.delete()
    messages.success(request, f"La receta '{receta.Nombre_Receta}' fue eliminada correctamente.")
    return redirect("ver_recetas")

@login_required
def calculadora_view(request):
    return render(request, "calculadora.html")
