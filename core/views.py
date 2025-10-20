from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Usuario, Rol, Historial, Comprobante, RecetaIngrediente, Receta, Ingrediente, UnidadMedicion
from .forms import RecetaForm, RecetaIngredienteForm, UnidadMedicionForm, IngredienteForm
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import Usuario, Rol
import json
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .models import Rol
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

Usuario = get_user_model()

# LOGIN
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


def register(request):
    if request.method == "POST":
        nombre = request.POST.get("nombre")
        correo = request.POST.get("correo")
        contraseña = request.POST.get("contraseña")
        rol_id = request.POST.get("rol")

        # Validación de campos
        if not nombre or not correo or not contraseña or not rol_id:
            messages.error(request, "Todos los campos son obligatorios")
            return redirect('register')

        # Verificar si ya existe el usuario
        if Usuario.objects.filter(username=nombre).exists():
            messages.error(request, "Nombre de usuario ya existe")
            return redirect('register')
        if Usuario.objects.filter(email=correo).exists():
            messages.error(request, "Correo ya registrado")
            return redirect('register')

        # Obtener rol
        try:
            rol = Rol.objects.get(id=rol_id)
        except Rol.DoesNotExist:
            messages.error(request, "Rol seleccionado no existe")
            return redirect('register')

        # Crear usuario
        user = Usuario.objects.create_user(
            username=nombre,
            email=correo,
            password=contraseña,
            rol=rol  
        )

        messages.success(request, "Usuario creado exitosamente")
        return redirect('home')

    # GET → mostrar formulario
    roles = Rol.objects.all()
    return render(request, 'register.html', {'roles': roles})

@login_required
def dashboard(request):
    usuario = request.user  # request.user ya es un Usuario
    return render(request, "dashboard.html", {
        "nombre": usuario.username,  # o usuario.first_name si quieres usar nombre real
        "rol": usuario.rol  
    })

@login_required
def subir_receta(request):
    ingredientes = Ingrediente.objects.all()

    if request.method == "POST":
        receta_form = RecetaForm(request.POST, request.FILES)

        if receta_form.is_valid():
            receta = receta_form.save(commit=False)
            # receta.Usuario_IdUsuario = str(request.user)  <-- eliminado, no existe
            receta.save()

            # Procesar ingredientes
            ingredientes_json = request.POST.get('ingredientes_json', '[]')
            try:
                ingredientes_data = json.loads(ingredientes_json)
            except json.JSONDecodeError:
                ingredientes_data = []

            costo_total = Decimal(0)

            for ing in ingredientes_data:
                if not ing.get('id') or not ing.get('cantidad'):
                    continue

                ingrediente = Ingrediente.objects.get(idIngrediente=int(ing['id']))
                cantidad = Decimal(ing['cantidad'])
                unidad = ing.get('unidad', '')
                precio_unitario = Decimal(ing.get('precio', 0))
                calidad = ing.get('calidad', '')

                # Guardar ingrediente en la receta
                RecetaIngrediente.objects.create(
                    Receta_idReceta=receta.Nombre_Receta,
                    Ingrediente_idIngrediente=ingrediente.Nombre_Ingrediente,
                    Cantidad=cantidad
                )

                # Normalizar cantidad según unidad
                factor_conversion = {
                    'g': Decimal('0.001'),  # g → kg
                    'kg': Decimal('1'),
                    'ml': Decimal('0.001'), # ml → l
                    'l': Decimal('1')
                }
                cantidad_normalizada = cantidad * factor_conversion.get(unidad, 1)
                costo_total += precio_unitario * cantidad_normalizada

            # Calcular precio final
            factor_multiplicacion = Decimal(1.3)
            iva = Decimal(0.19)
            precio_bruto = costo_total * factor_multiplicacion * (1 + iva)

            # Guardar comprobante
            Comprobante.objects.create(
                Receta=receta.Nombre_Receta,
                Costo_Total=int(costo_total),
                Factor_Multiplicacion=factor_multiplicacion,
                Iva=iva,
                Precio_Bruto=int(precio_bruto)
            )

            # Guardar historial
            Historial.objects.create(
                Usuario=str(request.user),          
                Receta=receta.Nombre_Receta,        
                Cambio_Realizado=f"Receta '{receta.Nombre_Receta}' creada."
            )

            messages.success(request, "Receta subida exitosamente.")
            return redirect("ver_recetas")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        receta_form = RecetaForm()

    return render(request, "subir_receta.html", {
        "receta_form": receta_form,
        "ingredientes": ingredientes
    })


# views.py
@login_required
def ver_recetas(request):
    usuario = str(request.user)
    # Obtenemos los nombres de recetas que este usuario subió según historial
    recetas_nombres = Historial.objects.filter(Usuario=usuario).values_list('Receta', flat=True).distinct()

    recetas = Receta.objects.filter(Nombre_Receta__in=recetas_nombres)

    recetas_data = []
    for receta in recetas:
        ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=receta.Nombre_Receta)

        ingredientes_info = []
        for ri in ingredientes:
            try:
                ingrediente = Ingrediente.objects.get(Nombre_Ingrediente=ri.Ingrediente_idIngrediente)
                ingredientes_info.append({
                    "Cantidad": ri.Cantidad,
                    "Nombre": ingrediente.Nombre_Ingrediente,
                    "Unidad": ingrediente.UnidadMedicion_idUnidadMedicion,
                    "Precio": ingrediente.Costo_Unitario,
                    "Calidad": ingrediente.Calidad
                })
            except Ingrediente.DoesNotExist:
                ingredientes_info.append({
                    "Cantidad": ri.Cantidad,
                    "Nombre": ri.Ingrediente_idIngrediente,
                    "Unidad": "N/A",
                    "Precio": 0,
                    "Calidad": "Desconocida"
                })

        try:
            comprobante = Comprobante.objects.get(Receta=receta.Nombre_Receta)
            precio = comprobante.Precio_Bruto
        except Comprobante.DoesNotExist:
            precio = "No calculado"

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes_info,
            "precio": precio,
        })

    return render(request, "ver_recetas.html", {"recetas_data": recetas_data})


@login_required
def editar_receta(request, idReceta):
    # Obtener la receta
    receta = get_object_or_404(Receta, pk=idReceta)

    # Solo el dueño puede editar
    if receta.Usuario_IdUsuario != request.user:
        return HttpResponseForbidden("No tienes permiso para editar esta receta.")

    ingredientes = Ingrediente.objects.all()  # todos los ingredientes posibles
    receta_ingredientes = receta.receta_ingredientes.all()
    unidades = UnidadMedicion.objects.all()  # todas las unidades disponibles

    if request.method == "POST":
        receta_form = RecetaForm(request.POST, request.FILES, instance=receta)

        if receta_form.is_valid():
            receta_form.save()

            # Procesar ingredientes
            ingredientes_json = request.POST.get('ingredientes_json', '[]')
            try:
                ingredientes_data = json.loads(ingredientes_json)
            except json.JSONDecodeError:
                ingredientes_data = []

            # Borrar los ingredientes antiguos
            receta.receta_ingredientes.all().delete()

            costo_total = Decimal(0)

            for ing in ingredientes_data:
                if not ing.get('id') or not ing.get('cantidad') or not ing.get('unidad'):
                    continue

                ingrediente = Ingrediente.objects.get(IdIngrediente=int(ing['id']))
                cantidad = Decimal(ing['cantidad'])

                # Guardar ingrediente con unidad editable
                RecetaIngrediente.objects.create(
                    Receta_idReceta=receta,
                    Ingrediente_IdIngrediente=ingrediente,
                    Cantidad=cantidad
                )

                # Normalizar cantidad según unidad original del ingrediente
                unidad_original = ingrediente.UnidadMedicion_idUnidadMedicion.Abreviatura
                factor_conversion = {
                    'g': Decimal('0.001'),  # g → kg
                    'kg': Decimal('1'),
                    'cda': Decimal('0.001'),
                    'ml': Decimal('0.001'), # ml → l
                    'l': Decimal('1')
                }
                cantidad_normalizada = cantidad * factor_conversion.get(unidad_original, 1)
                costo_total += Decimal(ingrediente.Costo_Unitario) * cantidad_normalizada

            # Actualizar comprobante
            factor_multiplicacion = Decimal(1.3)
            iva = Decimal(0.19)
            precio_bruto = costo_total * factor_multiplicacion * (1 + iva)

            comprobante, created = Comprobante.objects.get_or_create(Receta_idReceta=receta)
            comprobante.Costo_Total = costo_total
            comprobante.Factor_Multiplicacion = factor_multiplicacion
            comprobante.Iva = iva
            comprobante.Precio_Bruto = precio_bruto
            comprobante.save()

            # Registrar historial
            Historial.objects.create(
                Usuario_IdUsuario=request.user,
                Receta_IdReceta=receta,
                Cambio_Realizado=f"Receta '{receta.Nombre_Receta}' actualizada."
            )

            messages.success(request, "Receta actualizada exitosamente.")
            return redirect("ver_recetas")
        else:
            messages.error(request, "Corrige los errores en el formulario.")
    else:
        receta_form = RecetaForm(instance=receta)

    return render(request, "editar_receta.html", {
        "receta": receta,
        "receta_form": receta_form,
        "ingredientes": ingredientes,
        "receta_ingredientes": receta_ingredientes,
        "unidades": unidades  # <-- PASAMOS LAS UNIDADES
    })
@login_required
def borrar_receta(request, idReceta):
    receta = get_object_or_404(Receta, pk=idReceta)
    usuario_actual = str(request.user)

    # Traer todas las relaciones receta-ingrediente
    receta_ingredientes_raw = RecetaIngrediente.objects.filter(
        Receta_idReceta=str(receta.idReceta)
    )

    ingredientes_detallados = []
    for ri in receta_ingredientes_raw:
        ingrediente = None
        unidad = None

        # Buscar ingrediente por nombre, ignorando mayúsculas/minúsculas
        ingrediente = Ingrediente.objects.filter(
            Nombre_Ingrediente__iexact=ri.Ingrediente_idIngrediente
        ).first()

        # Obtener unidad si el campo es numérico
        if ingrediente:
            if ingrediente.UnidadMedicion_idUnidadMedicion.isdigit():
                unidad = UnidadMedicion.objects.filter(
                    idUnidadMedicion=int(ingrediente.UnidadMedicion_idUnidadMedicion)
                ).first()

        # Agregar al listado de ingredientes
        ingredientes_detallados.append({
            "nombre": ingrediente.Nombre_Ingrediente if ingrediente else ri.Ingrediente_idIngrediente,
            "cantidad": ri.Cantidad,
            "unidad": unidad.Abreviatura if unidad else "—",
            "precio": ingrediente.Costo_Unitario if ingrediente else "No encontrado"
        })

    # POST: confirmar borrado
    if request.method == "POST":
        nombre_receta = receta.Nombre_Receta

        # Borrar relaciones e historial
        RecetaIngrediente.objects.filter(Receta_idReceta=str(receta.idReceta)).delete()
        Comprobante.objects.filter(Receta=nombre_receta).delete()

        Historial.objects.create(
            Usuario=usuario_actual,
            Receta=nombre_receta,
            Cambio_Realizado=f"La receta '{nombre_receta}' fue eliminada."
        )

        # Borrar receta principal
        receta.delete()

        messages.success(request, f"La receta '{nombre_receta}' fue eliminada correctamente.")
        return redirect("ver_recetas")

    # Contexto para el template
    return render(request, "borrar_receta.html", {
        "receta": receta,
        "ingredientes": ingredientes_detallados,
        "imagen": receta.Imagen.url if receta.Imagen else None,
    })

@login_required
def comprobante_receta(request, idReceta):
    # 1) Obtener la receta (por idReceta)
    try:
        receta = Receta.objects.get(idReceta=idReceta)
    except Receta.DoesNotExist:
        return render(request, 'error.html', {'mensaje': 'Receta no encontrada'})

    # 2) Permisos: permitir al creador o a un profesor
    usuario_actual = request.user
    rol_actual = (getattr(usuario_actual, 'rol', '') or '').lower()

    # Intentamos obtener el owner id guardado en la receta (si existe)
    dueño_id = None
    if hasattr(receta, 'Usuario_IdUsuario'):
        try:
            dueño_id = int(getattr(receta, 'Usuario_IdUsuario'))
        except (TypeError, ValueError):
            dueño_id = None

    # Si no es profesor y no es el dueño -> denegar
    if rol_actual != 'profesor' and dueño_id != usuario_actual.id:
        return HttpResponseForbidden("No tienes permiso para ver este comprobante.")

    # 3) Buscar comprobante: como en tu modelo Comprobante la columna es 'Receta' (char),
    #   probamos varias estrategias para encontrar el comprobante correcto.
    comprobante = None
    # a) buscar por nombre de receta
    comprobante = Comprobante.objects.filter(Receta=receta.Nombre_Receta).first()
    # b) si no, buscar por id (string/int)
    if not comprobante:
        comprobante = Comprobante.objects.filter(Receta=str(receta.idReceta)).first()
    # c) si no, buscar por contiene (por si guardaron "Receta 3" u otro formato)
    if not comprobante:
        comprobante = Comprobante.objects.filter(Receta__icontains=str(receta.idReceta)).first()

    # 4) Traer ingredientes relacionados (RecetaIngrediente almacena Receta_idReceta como CharField)
    posibles_ri = RecetaIngrediente.objects.filter(Receta_idReceta__in=[str(receta.idReceta), receta.Nombre_Receta])
    # si no hay matches exactos, tomar todos los que tengan receta.nombre en el campo
    if not posibles_ri.exists():
        posibles_ri = RecetaIngrediente.objects.filter(Receta_idReceta__icontains=str(receta.idReceta))

    ingredientes_list = []
    for ri in posibles_ri:
        # intentamos resolver el ingrediente real (si guardaron id o nombre)
        ingrediente_obj = None
        nombre_ingrediente = None
        costo_unit = None

        val_ing = ri.Ingrediente_idIngrediente
        # si val_ing parece un número -> buscar por id
        try:
            ing_id = int(val_ing)
            ingrediente_obj = Ingrediente.objects.filter(idIngrediente=ing_id).first()
        except Exception:
            ingrediente_obj = None

        if ingrediente_obj:
            nombre_ingrediente = ingrediente_obj.Nombre_Ingrediente
            # Costo_Unitario es DecimalField en tu modelo Ingrediente
            costo_unit = ingrediente_obj.Costo_Unitario
            unidad = ingrediente_obj.UnidadMedicion_idUnidadMedicion
        else:
            # si no encontramos objeto, usamos el texto que esté en el campo
            nombre_ingrediente = val_ing
            unidad = getattr(ri, 'Unidad', None) or ''  # por si hay algo
            costo_unit = None

        # subtotal (si tenemos costo unitario)
        subtotal = None
        try:
            cantidad = ri.Cantidad
            if costo_unit is not None:
                subtotal = cantidad * Decimal(costo_unit)
        except Exception:
            subtotal = None

        ingredientes_list.append({
            'raw': ri,
            'nombre': nombre_ingrediente,
            'cantidad': ri.Cantidad,
            'unidad': unidad,
            'costo_unit': costo_unit,
            'subtotal': subtotal,
        })

    # 5) Render con context robusto
    return render(request, 'comprobante_receta.html', {
        'receta': receta,
        'comprobante': comprobante,
        'ingredientes': ingredientes_list,
    })

@login_required
def perfil_view(request):
    usuario = request.user  # tu modelo Usuario personalizado

    if request.method == "POST":
        # Solo actualizar nombre y correo
        usuario.username = request.POST.get("username")
        usuario.email = request.POST.get("email")
        usuario.save()
        messages.success(request, "Perfil actualizado correctamente.")
        return redirect('perfil')

    return render(request, 'perfil.html', {
        'usuario': usuario,
        'rol': usuario.rol  # solo para mostrarlo como texto
    })

def ver_historial(request):
    historial = Historial.objects.all().order_by('-Fecha_Modificacion')
    return render(request, 'ver_historial.html', {'historial': historial})


class CambiarContraseñaView(PasswordChangeView):
    template_name = 'cambiar_contraseña.html'
    success_url = reverse_lazy('perfil')

    def form_valid(self, form):
        messages.success(self.request, "Tu contraseña se cambió correctamente.")
        return super().form_valid(form)


def calculadora_view(request):
    return render(request, 'calculadora.html')

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
            return redirect("dashboard")  # redirige al panel principal
    else:
        form = IngredienteForm()
    return render(request, "crear_ingrediente.html", {"form": form})

def ver_ingredientes(request):
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para ver los ingredientes.")

    ingredientes = Ingrediente.objects.all()
    unidades = {u.idUnidadMedicion: u for u in UnidadMedicion.objects.all()}

    for ing in ingredientes:
        id_unidad = ing.UnidadMedicion_idUnidadMedicion
        ing.unidad_nombre = unidades.get(int(id_unidad)).Nombre_Unidad if id_unidad.isdigit() and int(id_unidad) in unidades else id_unidad

    return render(request, "ver_ingredientes.html", {"ingredientes": ingredientes})


@login_required
def crear_unidad_medicion(request):
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    if request.method == "POST":
        form = UnidadMedicionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("dashboard")
    else:
        form = UnidadMedicionForm()
    return render(request, "crear_unidad_medicion.html", {"form": form})

@login_required
def ver_recetas_alumnos(request):
    # Solo los profesores pueden acceder
    if not solo_profesor(request.user):
        return HttpResponseForbidden("No tienes permiso para ver esta página.")

    # Traemos todas las recetas
    recetas = Receta.objects.all()  # sin select_related ni prefetch_related

    recetas_data = []
    for receta in recetas:
        # Obtener ingredientes relacionados manualmente
        ingredientes = RecetaIngrediente.objects.filter(Receta_idReceta=str(receta.idReceta))

        # Obtener comprobante si existe
        comprobante = Comprobante.objects.filter(Receta=receta.Nombre_Receta).first()
        precio = comprobante.Precio_Bruto if comprobante else "No calculado"

        # Usuario asociado como texto
        usuario_texto = getattr(receta, "Usuario", "Desconocido")  # si tienes un campo Usuario

        recetas_data.append({
            "receta": receta,
            "ingredientes": ingredientes,
            "precio": precio,
            "usuario": usuario_texto
        })

    return render(request, "ver_recetas_alumnos.html", {"recetas_data": recetas_data})
