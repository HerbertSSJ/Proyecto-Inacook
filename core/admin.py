from django.contrib import admin
from .models import (
    Usuario, Rol, Receta, Ingrediente,
    RecetaIngrediente, Comprobante, Historial, UnidadMedicion
)

# -------------------- ROL --------------------
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("id", "NombreRol")
    search_fields = ("NombreRol",)
    ordering = ("NombreRol",)


# -------------------- USUARIO --------------------
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "rol", "is_active", "is_staff")
    search_fields = ("username", "email", "rol")
    list_filter = ("rol", "is_staff", "is_active")
    ordering = ("username",)


# -------------------- UNIDAD DE MEDICIÓN --------------------
@admin.register(UnidadMedicion)
class UnidadMedicionAdmin(admin.ModelAdmin):
    list_display = ("idUnidadMedicion", "Nombre_Unidad", "Abreviatura")
    search_fields = ("Nombre_Unidad", "Abreviatura")
    ordering = ("Nombre_Unidad",)


# -------------------- INGREDIENTE --------------------
@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ("idIngrediente", "Nombre_Ingrediente", "Calidad", "Costo_Unitario", "UnidadMedicion_idUnidadMedicion")
    search_fields = ("Nombre_Ingrediente", "Calidad")
    list_filter = ("Calidad", "UnidadMedicion_idUnidadMedicion")
    ordering = ("Nombre_Ingrediente",)


# -------------------- RECETA --------------------
@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ("idReceta", "Nombre_Receta", "Categoria", "Tiempo_Preparacion", "Aporte_Calorico")
    search_fields = ("Nombre_Receta", "Categoria")
    list_filter = ("Categoria",)
    ordering = ("Nombre_Receta",)


# -------------------- RECETA - INGREDIENTE --------------------
@admin.register(RecetaIngrediente)
class RecetaIngredienteAdmin(admin.ModelAdmin):
    list_display = ("idRecetaIngrediente", "Receta_idReceta", "Ingrediente_idIngrediente", "Cantidad")
    search_fields = ("Receta_idReceta", "Ingrediente_idIngrediente")
    ordering = ("Receta_idReceta",)


# -------------------- COMPROBANTE --------------------
@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ("IdComprobante", "Receta", "Costo_Total", "Precio_Bruto", "Iva")
    search_fields = ("Receta",)
    ordering = ("Receta",)


# -------------------- HISTORIAL --------------------
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ("idHistorial", "Usuario", "Receta", "Fecha_Modificacion", "Cambio_Realizado")
    search_fields = ("Usuario", "Receta", "Cambio_Realizado")
    list_filter = ("Fecha_Modificacion",)
    ordering = ("-Fecha_Modificacion",)
