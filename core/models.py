from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from django.db import models


class Rol(models.Model):
    NombreRol = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = "Rol"

    def __str__(self):
        return self.NombreRol


class Usuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey("Rol", on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "Usuario"

    def __str__(self):
        return self.user.username


class UnidadMedicion(models.Model):
    Nombre_Unidad = models.CharField(max_length=100)
    Abreviatura = models.CharField(max_length=15)

    class Meta:
        db_table = "UnidadMedicion"

    def __str__(self):
        return f"{self.Nombre_Unidad} ({self.Abreviatura})"


class Ingrediente(models.Model):
    Nombre_Ingrediente = models.CharField(max_length=100)
    Calidad = models.CharField(max_length=45)
    Costo_Unitario = models.IntegerField(validators=[MinValueValidator(0)])
    UnidadMedicion = models.ForeignKey(UnidadMedicion, on_delete=models.PROTECT)

    class Meta:
        db_table = "Ingrediente"

    def __str__(self):
        return self.Nombre_Ingrediente


class Receta(models.Model):
    Nombre_Receta = models.CharField(max_length=100)
    Categoria = models.CharField(max_length=45)
    Aporte_Calorico = models.IntegerField()
    Tiempo_Preparacion = models.CharField(max_length=45)
    imagen = models.ImageField(upload_to='recetas/', null=True, blank=True)
    Usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "Receta"

    def __str__(self):
        return self.Nombre_Receta


class RecetaIngrediente(models.Model):
    Receta = models.ForeignKey(Receta, on_delete=models.CASCADE)
    Ingrediente = models.ForeignKey(Ingrediente, on_delete=models.CASCADE)
    Cantidad = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = "RecetaIngrediente"

    def __str__(self):
        return f"{self.Cantidad} de {self.Ingrediente.Nombre_Ingrediente}"

class Comprobante(models.Model):
    Costo_Total = models.IntegerField()
    Factor_Multiplicacion = models.DecimalField(max_digits=10, decimal_places=4)
    Iva = models.DecimalField(max_digits=10, decimal_places=4)
    Precio_Bruto = models.IntegerField(validators=[MinValueValidator(0)])
    Receta = models.ForeignKey(Receta, on_delete=models.CASCADE)

    class Meta:
        db_table = "Comprobante"

    def __str__(self):
        return f"Comprobante #{self.id}"

class Historial(models.Model):
    Fecha_Entrega = models.DateTimeField(null=True, blank=True)
    Fecha_Modificacion = models.DateTimeField(auto_now=True)
    Usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    Receta = models.ForeignKey(Receta, on_delete=models.SET_NULL, null=True)
    Cambio_Realizado = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "Historial"

    def __str__(self):
        return f"Historial cambio #{self.id}"
