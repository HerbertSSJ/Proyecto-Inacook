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


class UnidadDeMedida(models.Model):
    nombre_unidad = models.CharField(max_length=45)
    abreviatura = models.CharField(max_length=45)

    def __str__(self):
        return f"{self.nombre_unidad} ({self.abreviatura})"


class Ingrediente(models.Model):
    nombre = models.CharField(max_length=100)
    calidad = models.CharField(max_length=45)
    unidad = models.IntegerField()
    costo_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    unidad_medida = models.ForeignKey(UnidadDeMedida, on_delete=models.CASCADE)

    def __str__(self):
        return self.nombre


class Preparacion(models.Model):
    nombre = models.CharField(max_length=100)
    categoria = models.CharField(max_length=45)
    aporte_calorico = models.IntegerField()
    tiempo_preparacion = models.IntegerField(help_text="Tiempo en minutos")

    def __str__(self):
        return self.nombre


class Procedimiento(models.Model):
    orden_paso = models.IntegerField()
    descripcion = models.TextField()
    preparacion = models.ForeignKey(Preparacion, on_delete=models.CASCADE, related_name="procedimientos")

    def __str__(self):
        return f"Paso {self.orden_paso} - {self.preparacion.nombre}"


class Costo(models.Model):
    costo_receta = models.DecimalField(max_digits=10, decimal_places=2)
    factor_multiplicacion = models.DecimalField(max_digits=5, decimal_places=2)
    iva = models.DecimalField(max_digits=5, decimal_places=2)
    precio_bruto = models.IntegerField()
    preparacion = models.ForeignKey(Preparacion, on_delete=models.CASCADE, related_name="costos")

    def __str__(self):
        return f"Costo de {self.preparacion.nombre}"


class Receta(models.Model):
    cantidad = models.IntegerField()
    costo_total = models.IntegerField()
    preparacion = models.ForeignKey(Preparacion, on_delete=models.CASCADE, related_name="recetas")
    ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE, related_name="recetas")

    def __str__(self):
        return f"Receta de {self.preparacion.nombre} con {self.ingrediente.nombre}"


class Historial(models.Model):
    fecha_modificacion = models.DateTimeField(auto_now=True)
    cambio_realizado = models.TextField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    preparacion = models.ForeignKey(Preparacion, on_delete=models.CASCADE)

    def __str__(self):
        return f"Historial de {self.preparacion.nombre} - {self.usuario.username}"