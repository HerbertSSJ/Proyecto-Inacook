from decimal import Decimal
import json

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from .models import (
    Usuario, Rol, Receta, Ingrediente,
    UnidadMedicion, RecetaIngrediente,
    Comprobante, Historial
)
from .forms import RecetaForm, IngredienteForm


# ============================================================
#   HELPERS
# ============================================================

def es_profesor(user):
    """Retorna True si el usuario tiene rol 'Profesor'."""
    if hasattr(user, "usuario") and user.usuario.rol:
        return user.usuario.rol.NombreRol.lower() == "profesor"
    return False


def cargar_json_seguro(data):
    try:
        return json.loads(data)
    except Exception:
        return []


def procesar_ingredientes(receta, ingredientes_json):
  
    costo_total = Decimal("0")

    for ing in ingredientes_json:
        if not ing.get("id") or not ing.get("cantidad"):
            continue

        # ---------- FIX PARA CANTIDADES CON COMA ----------
        cantidad_str = str(ing["cantidad"]).replace(",", ".").strip()

        try:
            cantidad = Decimal(cantidad_str)
        except:
            cantidad = Decimal("0")

        # Obtener ingrediente
        try:
            ingrediente = Ingrediente.objects.get(id=int(ing["id"]))
        except Ingrediente.DoesNotExist:
            continue

        precio_unitario = Decimal(str(ingrediente.Costo_Unitario))

        # Guardar relación N-M
        RecetaIngrediente.objects.create(
            Receta=receta,
            Ingrediente=ingrediente,
            Cantidad=cantidad
        )

        # Acumular costo
        costo_total += cantidad * precio_unitario

    return costo_total



# ============================================================
#   LOGIN
# ============================================================

def home(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        contraseña = request.POST.get("contraseña", "").strip()

        user = authenticate(request, username=nombre, password=contraseña)

        if user:
            login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Usuario o contraseña incorrectos.")
            return redirect("home")

    return render(request, "login.html")


# ============================================================
#   REGISTRO
# ============================================================

def register(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre", "").strip()
        correo = request.POST.get("correo", "").strip()
        contraseña = request.POST.get("contraseña", "")
        rol_id = request.POST.get("rol")

        # Validaciones
        if not all([nombre, correo, contraseña, rol_id]):
            messages.error(request, "Todos los campos son obligatorios.")
            return redirect("register")

        if User.objects.filter(username=nombre).exists():
            messages.error(request, "El nombre de usuario ya está registrado.")
            return redirect("register")

        if User.objects.filter(email=correo).exists():
            messages.error(request, "El correo ya está registrado.")
            return redirect("register")

        # Crear usuario Django
        user = User.objects.create_user(
            username=nombre,
            email=correo,
            password=contraseña
        )

        rol = Rol.objects.get(id=rol_id)

        # Crear perfil
        Usuario.objects.create(
            user=user,
            rol=rol
        )

        messages.success(request, "Cuenta creada exitosamente.")
        return redirect("home")

    roles = Rol.objects.all()
    return render(request, "register.html", {"roles": roles})


# ============================================================
#   DASHBOARD
# ============================================================

@login_required
def dashboard(request):
    perfil = request.user.usuario
    return render(request, "dashboard.html", {
        "nombre": request.user.username,
        "rol": perfil.rol.NombreRol if perfil.rol else "Sin rol"
    })


# ============================================================
#   PERFIL
# ============================================================

@login_required
def perfil_view(request):
    usuario = request.user

    if request.method == "POST":
        usuario.username = request.POST.get("username", usuario.username)
        usuario.email = request.POST.get("email", usuario.email)
        usuario.save()

        messages.success(request, "Perfil actualizado correctamente.")
        return redirect("perfil")

    return render(request, "perfil.html", {"usuario": usuario})


class CambiarContraseñaView(PasswordChangeView):
    template_name = "cambiar_contraseña.html"
    success_url = reverse_lazy("perfil")

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña se cambió correctamente.")
        return super().form_valid(form)


# ============================================================
#   SUBIR RECETA
# ============================================================

@login_required
def subir_receta(request):
    ingredientes = Ingrediente.objects.select_related("UnidadMedicion").all()
    unidades = UnidadMedicion.objects.all()

    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES)

        if form.is_valid():
            receta = form.save(commit=False)
            receta.Usuario = request.user.usuario
            receta.save()

            ingredientes_json = cargar_json_seguro(
                request.POST.get("ingredientes_json", "[]")
            )
            costo_total = procesar_ingredientes(receta, ingredientes_json)

            factor = Decimal("1.3")
            iva = Decimal("0.19")
            precio_bruto = costo_total * factor * (1 + iva)

            Comprobante.objects.create(
                Receta=receta,
                Costo_Total=costo_total,
                Factor_Multiplicacion=factor,
                Iva=iva,
                Precio_Bruto=precio_bruto
            )

            # 🔵 AGREGAR AL HISTORIAL
            Historial.objects.create(
                Usuario=request.user.usuario,
                Receta=receta,
                Cambio_Realizado=f"Receta creada: {receta.Nombre_Receta}"
            )

            messages.success(request, "Receta subida exitosamente.")
            return redirect("ver_recetas")

        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RecetaForm()

    return render(request, "subir_receta.html", {
        "receta_form": form,
        "ingredientes": ingredientes,
        "unidades": unidades,
    })



# ============================================================
#   VER RECETAS (ALUMNO)
# ============================================================

@login_required
def ver_recetas(request):
    usuario = request.user.usuario
    recetas = Receta.objects.filter(Usuario=usuario)
    recetas_data = []

    for receta in recetas:
        rels = RecetaIngrediente.objects.select_related(
            "Ingrediente__UnidadMedicion"
        ).filter(Receta=receta)

        ingredientes_info = []
        for ri in rels:
            ingredientes_info.append({
                "Cantidad": ri.Cantidad,
                "Nombre": ri.Ingrediente.Nombre_Ingrediente,
                "Unidad": f"{ri.Ingrediente.UnidadMedicion.Nombre_Unidad} ({ri.Ingrediente.UnidadMedicion.Abreviatura})",
                "Precio": ri.Ingrediente.Costo_Unitario,
                "Calidad": ri.Ingrediente.Calidad,
                })

        comprobante = Comprobante.objects.filter(Receta=receta).first()
        precio = comprobante.Precio_Bruto if comprobante else "No calculado"

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes_info,
            "precio": precio
        })

    return render(request, "ver_recetas.html", {"recetas_data": recetas_data})


# ============================================================
#   VER RECETAS (PROFESOR)
# ============================================================

@login_required
def ver_recetas_alumnos(request):
    if not es_profesor(request.user):
        return redirect("dashboard")

   
    # Captura de filtros
    
    buscar = request.GET.get("buscar", "").strip()
    categoria_filtro = request.GET.get("categoria", "").strip()
    letra_filtro = request.GET.get("letra", "").strip()

   
    # Trae todas las recetas

    recetas = Receta.objects.select_related("Usuario__user").all()


    # Aplicar filtros dinámicos

    # Filtrar por texto (nombre receta)
    if buscar:
        recetas = recetas.filter(Nombre_Receta__icontains=buscar)

    # Filtrar por categoría exacta
    if categoria_filtro:
        recetas = recetas.filter(Categoria=categoria_filtro)

    # Filtrar por letra inicial del nombre
    if letra_filtro:
        recetas = recetas.filter(Nombre_Receta__istartswith=letra_filtro)

   
    # Lista de categorías únicas
    
    categorias = Receta.objects.values_list("Categoria", flat=True).distinct()

    
    # Armar los datos para el HTML
   
    recetas_data = []

    for receta in recetas:

        ingredientes = RecetaIngrediente.objects.select_related(
            "Ingrediente__UnidadMedicion"
        ).filter(Receta=receta)

        comprobante = Comprobante.objects.filter(Receta=receta).first()
        precio = comprobante.Precio_Bruto if comprobante else "No calculado"

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes,
            "precio": precio,
            "usuario": receta.Usuario.user.username if receta.Usuario else "Desconocido"
        })

    return render(
        request,
        "ver_recetas_alumnos.html",
        {
            "recetas_data": recetas_data,
            "categorias": categorias,
        }
    )


# ============================================================
#   BORRAR RECETA
# ============================================================

@login_required
def borrar_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)

    if receta.Usuario != request.user.usuario:
        messages.error(request, "No puedes borrar esta receta.")
        return redirect("ver_recetas")

    #  AGREGAR AL HISTORIAL ANTES DE BORRAR
    Historial.objects.create(
        Usuario=request.user.usuario,
        Receta=receta,
        Cambio_Realizado=f"Receta eliminada: {receta.Nombre_Receta}"
    )

    receta.delete()
    messages.success(request, "Receta eliminada correctamente.")
    return redirect("ver_recetas")


# ============================================================
#   EDITAR RECETA (CON HISTORIAL REAL)
# ============================================================

@login_required
def editar_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)

    if receta.Usuario != request.user.usuario and not es_profesor(request.user):
        messages.error(request, "No tienes permiso para editar esta receta.")
        return redirect("ver_recetas")

    ingredientes = Ingrediente.objects.select_related("UnidadMedicion").all()
    unidades = UnidadMedicion.objects.all()
    receta_ingredientes = RecetaIngrediente.objects.filter(Receta=receta)

    # -------------------------------------------------------
    # GUARDAR ESTADO ANTERIOR PARA COMPARAR
    # -------------------------------------------------------
    antes = {
        "Nombre_Receta": receta.Nombre_Receta,
        "Categoria": receta.Categoria,
        "Aporte_Calorico": receta.Aporte_Calorico,
        "Tiempo_Preparacion": receta.Tiempo_Preparacion,
        "ingredientes": {
            ri.Ingrediente.id: {
                "nombre": ri.Ingrediente.Nombre_Ingrediente,
                "cantidad": float(ri.Cantidad),
                "unidad": ri.Ingrediente.UnidadMedicion.Abreviatura,
            }
            for ri in receta_ingredientes
        }
    }

    # helper interno para normalizar cantidades "12,00" -> 12.0
    def parse_cantidad(valor):
        if valor is None or valor == "":
            return None
        valor_str = str(valor).replace(",", ".").strip()
        try:
            return float(valor_str)
        except ValueError:
            return None

    if request.method == "POST":
        form = RecetaForm(request.POST, request.FILES, instance=receta)

        if form.is_valid():

            # -------------------------------------------------------
            # NOMBRE DUPLICADO PERO PERMITIDO
            # -------------------------------------------------------
            nuevo_nombre = form.cleaned_data["Nombre_Receta"].strip().title()
            usuario = request.user.usuario

            existe_otra = Receta.objects.filter(
                Usuario=usuario,
                Nombre_Receta=nuevo_nombre
            ).exclude(pk=receta.pk)

            if existe_otra.exists():
                messages.warning(
                    request,
                    f"Ya tienes otra receta llamada '{nuevo_nombre}', "
                    "pero puedes tener versiones distintas."
                )

            # Guardamos siempre la receta
            receta_actualizada = form.save()

            # -------------------------------------------------------
            # PROCESAR INGREDIENTES NUEVOS
            # -------------------------------------------------------
            ingredientes_json = cargar_json_seguro(
                request.POST.get("ingredientes_json", "[]")
            )

            RecetaIngrediente.objects.filter(Receta=receta).delete()
            procesar_ingredientes(receta, ingredientes_json)

            # -------------------------------------------------------
            # GUARDAR ESTADO NUEVO PARA COMPARAR
            # -------------------------------------------------------
            despues_ing = {}
            for ing in ingredientes_json:
                ing_id = ing.get("id")
                if not ing_id:
                    continue

                cantidad_norm = parse_cantidad(ing.get("cantidad"))
                if cantidad_norm is None:
                    continue

                despues_ing[str(ing_id)] = {
                    "nombre": ing.get("nombre", ""),
                    "cantidad": cantidad_norm,
                    "unidad": ing.get("unidad", "")
                }

            cambios = []

            # -------------------------------------------------------
            # CAMBIOS EN CAMPOS PRINCIPALES
            # -------------------------------------------------------
            if antes["Nombre_Receta"] != receta.Nombre_Receta:
                cambios.append(
                    f"Nombre: '{antes['Nombre_Receta']}' → '{receta.Nombre_Receta}'"
                )

            if antes["Categoria"] != receta.Categoria:
                cambios.append(
                    f"Categoría: '{antes['Categoria']}' → '{receta.Categoria}'"
                )

            if antes["Aporte_Calorico"] != receta.Aporte_Calorico:
                cambios.append(
                    f"Aporte calórico: {antes['Aporte_Calorico']} → {receta.Aporte_Calorico}"
                )

            if antes["Tiempo_Preparacion"] != receta.Tiempo_Preparacion:
                cambios.append(
                    f"Tiempo de preparación: '{antes['Tiempo_Preparacion']}' → '{receta.Tiempo_Preparacion}'"
                )

            # -------------------------------------------------------
            # CAMBIOS EN INGREDIENTES
            # -------------------------------------------------------
            for ing_id, ing_data in antes["ingredientes"].items():
                if str(ing_id) not in despues_ing:
                    cambios.append(f"Ingrediente eliminado: {ing_data['nombre']}")

            for ing_id, ing_data in despues_ing.items():
                if int(ing_id) not in antes["ingredientes"]:
                    cambios.append(
                        f"Ingrediente agregado: {ing_data['nombre']} "
                        f"({ing_data['cantidad']} {ing_data['unidad']})"
                    )

            for ing_id, ing_data in despues_ing.items():
                if int(ing_id) in antes["ingredientes"]:
                    antes_ing = antes["ingredientes"][int(ing_id)]

                    if ing_data["cantidad"] != antes_ing["cantidad"]:
                        cambios.append(
                            f"Cantidad modificada ({ing_data['nombre']}): "
                            f"{antes_ing['cantidad']} → {ing_data['cantidad']}"
                        )

                    if ing_data["unidad"] != antes_ing["unidad"]:
                        cambios.append(
                            f"Unidad modificada ({ing_data['nombre']}): "
                            f"{antes_ing['unidad']} → {ing_data['unidad']}"
                        )

            # -------------------------------------------------------
            # REGISTRAR HISTORIAL SOLO SI HUBO CAMBIOS
            # -------------------------------------------------------
            if cambios:
                Historial.objects.create(
                    Usuario=request.user.usuario,
                    Receta=receta,
                    Cambio_Realizado="; ".join(cambios)
                )

            messages.success(request, "Receta actualizada correctamente.")
            return redirect("ver_recetas")

        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = RecetaForm(instance=receta)

    return render(request, "editar_receta.html", {
        "receta_form": form,
        "receta": receta,
        "ingredientes": ingredientes,
        "unidades": unidades,
        "receta_ingredientes": receta_ingredientes
    })



# ============================================================
#   CREAR INGREDIENTE
# ============================================================

@login_required
def crear_ingrediente(request):
    if not es_profesor(request.user):
        return redirect("dashboard")

    if request.method == "POST":
        form = IngredienteForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, "Ingrediente creado exitosamente.")
            return redirect("ver_ingredientes")

        messages.error(request, "Corrige los errores del formulario.")
    else:
        form = IngredienteForm()

    return render(request, "crear_ingrediente.html", {"form": form})


# ============================================================
#   VER INGREDIENTES
# ============================================================

@login_required
def ver_ingredientes(request):
    if not es_profesor(request.user):
        return redirect("dashboard")

    ingredientes = Ingrediente.objects.select_related("UnidadMedicion").all()
    return render(request, "ver_ingredientes.html", {"ingredientes": ingredientes})


# ============================================================
#   EDITAR INGREDIENTES
# ============================================================

@login_required
def editar_ingrediente(request, id):
    if not es_profesor(request.user):
        return redirect("dashboard")

    ingrediente = get_object_or_404(Ingrediente, id=id)

    if request.method == "POST":
        form = IngredienteForm(request.POST, instance=ingrediente)

        if form.is_valid():
            form.save()
            messages.success(request, "Ingrediente actualizado correctamente.")
            return redirect("ver_ingredientes")
        else:
            messages.error(request, "Corrige los errores del formulario.")
    else:
        form = IngredienteForm(instance=ingrediente)

    return render(request, "editar_ingrediente.html", {"form": form, "ingrediente": ingrediente})

# ============================================================
#   ELIMINAR INGREDIENTES
# ============================================================

@login_required
def eliminar_ingrediente(request, id):
    if not es_profesor(request.user):
        return redirect("dashboard")

    ingrediente = get_object_or_404(Ingrediente, id=id)

    if request.method == "POST":
        ingrediente.delete()
        messages.success(request, "Ingrediente eliminado correctamente.")
        return redirect("ver_ingredientes")

    return render(request, "eliminar_ingrediente.html", {"ingrediente": ingrediente})


# ============================================================
#   HISTORIAL
# ============================================================

@login_required
def ver_historial(request):
    historial = Historial.objects.filter(
        Usuario=request.user.usuario
    ).order_by("-Fecha_Modificacion")

    return render(request, "ver_historial.html", {"historial": historial})


# ============================================================
#   COMPROBANTE DE RECETA
# ============================================================

@login_required
def comprobante_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)

    relaciones = RecetaIngrediente.objects.select_related(
        "Ingrediente__UnidadMedicion"
    ).filter(Receta=receta)

    ingredientes_detalle = []
    subtotal = Decimal("0")

    for ri in relaciones:
        precio_unitario = Decimal(ri.Ingrediente.Costo_Unitario)
        sub = precio_unitario * ri.Cantidad
        subtotal += sub

        ingredientes_detalle.append({
            "nombre": ri.Ingrediente.Nombre_Ingrediente,
            "cantidad": ri.Cantidad,
            "unidad": ri.Ingrediente.UnidadMedicion.Abreviatura,
            "precio_unitario": precio_unitario,
            "subtotal": sub,
        })

    comprobante = Comprobante.objects.filter(Receta=receta).first()

    iva_monto = Decimal("0")
    total_final = Decimal("0")

    if comprobante:
        iva_monto = subtotal * comprobante.Iva
        total_final = subtotal * comprobante.Factor_Multiplicacion + iva_monto

    return render(request, "comprobante_receta.html", {
        "receta": receta,
        "ingredientes_detalle": ingredientes_detalle,
        "subtotal": subtotal,
        "iva_monto": iva_monto,
        "total_final": total_final,
        "comprobante": comprobante,
    })


# ============================================================
#   CALCULADORA
# ============================================================

@login_required
def calculadora_view(request):
    return render(request, "calculadora.html")
