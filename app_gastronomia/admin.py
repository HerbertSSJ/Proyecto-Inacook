from django.contrib import admin
from .models import Platillo, UnidadDeMedida, Ingrediente, Preparacion, Procedimiento, Costo, Receta, Historial

admin.site.register(Platillo)
admin.site.register(UnidadDeMedida)
admin.site.register(Ingrediente)
admin.site.register(Preparacion)
admin.site.register(Procedimiento)
admin.site.register(Costo)
admin.site.register(Receta)
admin.site.register(Historial)