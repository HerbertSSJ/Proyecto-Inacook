from django.db import models
from django.contrib.auth.models import User

class Platillo(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    precio = models.FloatField()
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.URLField(blank=True, null=True)
    ingredientes = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre