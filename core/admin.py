from django.contrib import admin
from .models import Usuario, Rol, Receta, Ingrediente, RecetaIngrediente, Comprobante, Historial, UnidadMedicion

admin.site.register(Usuario)
admin.site.register(Rol)
admin.site.register(Receta)
admin.site.register(Ingrediente)
admin.site.register(RecetaIngrediente)
admin.site.register(Comprobante)
admin.site.register(Historial)
admin.site.register(UnidadMedicion)
