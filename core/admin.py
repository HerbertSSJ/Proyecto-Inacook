from django.contrib import admin
from .models import (
    Rol, Usuario, UnidadMedicion, Ingrediente,
    Receta, RecetaIngrediente, Comprobante, Historial
)


# ============================
#           ROL
# ============================
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id', 'NombreRol')
    search_fields = ('NombreRol',)


# ============================
#         USUARIO
# ============================
@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_username', 'get_email', 'rol')
    list_filter = ('rol',)
    search_fields = ('user__username', 'user__email')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Nombre de Usuario"

    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = "Correo"


# ============================
#   UNIDAD DE MEDICIÓN
# ============================
@admin.register(UnidadMedicion)
class UnidadMedicionAdmin(admin.ModelAdmin):
    list_display = ('id', 'Nombre_Unidad', 'Abreviatura')
    search_fields = ('Nombre_Unidad', 'Abreviatura')


# ============================
#       INGREDIENTE
# ============================
@admin.register(Ingrediente)
class IngredienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'Nombre_Ingrediente', 'Calidad', 'Costo_Unitario', 'UnidadMedicion')
    list_filter = ('Calidad', 'UnidadMedicion')
    search_fields = ('Nombre_Ingrediente',)


# ============================
#          RECETA
# ============================
@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    list_display = ('id', 'Nombre_Receta', 'Categoria', 'Aporte_Calorico', 'Tiempo_Preparacion', 'Usuario')
    list_filter = ('Categoria',)
    search_fields = ('Nombre_Receta',)


# ============================
#   RECETA INGREDIENTE
# ============================
@admin.register(RecetaIngrediente)
class RecetaIngredienteAdmin(admin.ModelAdmin):
    list_display = ('id', 'Receta', 'Ingrediente', 'Cantidad')
    search_fields = ('Receta__Nombre_Receta', 'Ingrediente__Nombre_Ingrediente')


# ============================
#        COMPROBANTE
# ============================
@admin.register(Comprobante)
class ComprobanteAdmin(admin.ModelAdmin):
    list_display = ('id', 'Receta', 'Costo_Total', 'Factor_Multiplicacion', 'Iva', 'Precio_Bruto')
    search_fields = ('Receta__Nombre_Receta',)


# ============================
#         HISTORIAL
# ============================
@admin.register(Historial)
class HistorialAdmin(admin.ModelAdmin):
    list_display = ('id', 'Usuario', 'Receta', 'Fecha_Modificacion', 'Cambio_Realizado')
    list_filter = ('Fecha_Modificacion',)
    search_fields = ('Usuario__user__username', 'Receta__Nombre_Receta')
