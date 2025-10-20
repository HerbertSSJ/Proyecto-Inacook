from django.db import models
from django.contrib.auth.models import AbstractUser
# -------------------- ROL --------------------
class Rol(models.Model):
    NombreRol = models.CharField(max_length=45, unique=True)

    class Meta:
        db_table = 'Rol'  # 👈 nombre exacto en la BD

    def __str__(self):
        return self.NombreRol


# -------------------- USUARIO --------------------
class Usuario(AbstractUser):
    rol = models.CharField(max_length=45, db_column='Rol', blank=True, null=True, default="Sin rol")

    class Meta:
        db_table = 'Usuario' 

    def __str__(self):
        return self.username


# -------------------- UNIDAD DE MEDICIÓN --------------------
class UnidadMedicion(models.Model):
    idUnidadMedicion = models.AutoField(primary_key=True, db_column='idUnidadMedicion')
    Nombre_Unidad = models.CharField(max_length=100, default="Sin unidad", db_column='Nombre_Unidad')
    Abreviatura = models.CharField(max_length=10, default="NA", db_column='Abreviatura')

    class Meta:
        db_table = 'UnidadMedicion'  # 👈 nombre exacto

    def __str__(self):
        return self.Abreviatura


# -------------------- INGREDIENTE --------------------
class Ingrediente(models.Model):
    idIngrediente = models.AutoField(primary_key=True, db_column='idIngrediente')
    Nombre_Ingrediente = models.CharField(max_length=100, default="Ingrediente genérico", db_column='Nombre_Ingrediente')
    Calidad = models.CharField(max_length=45, default="Normal", db_column='Calidad')
    Costo_Unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Costo_Unitario')
    UnidadMedicion_idUnidadMedicion = models.CharField(max_length=100, default="Unidad", db_column='UnidadMedicion_idUnidadMedicion')

    class Meta:
        db_table = 'Ingrediente'  # 👈 nombre exacto

    def __str__(self):
        return self.Nombre_Ingrediente


# -------------------- RECETA --------------------
class Receta(models.Model):
    idReceta = models.AutoField(primary_key=True, db_column='idReceta')
    Nombre_Receta = models.CharField(max_length=100, default="Receta genérica", db_column='Nombre_Receta')
    Categoria = models.CharField(max_length=45, default="Sin categoría", db_column='Categoria')
    Aporte_Calorico = models.IntegerField(default=0, db_column='Aporte_Calorico')
    Tiempo_Preparacion = models.CharField(max_length=45, default="0 min", db_column='Tiempo_Preparacion')
    Procedimiento = models.TextField(default="Sin procedimiento", db_column='Procedimiento')
    Imagen = models.ImageField(upload_to="recetas/", null=True, blank=True, db_column='Imagen')

    class Meta:
        db_table = 'Receta'  # 👈 nombre exacto

    def __str__(self):
        return self.Nombre_Receta


# -------------------- RELACIÓN RECETA - INGREDIENTE --------------------
class RecetaIngrediente(models.Model):
    idRecetaIngrediente = models.AutoField(primary_key=True, db_column='idRecetaIngrediente')
    Receta_idReceta = models.CharField(max_length=100, default="Receta genérica", db_column='Receta_idReceta')
    Ingrediente_idIngrediente = models.CharField(max_length=100, default="Ingrediente genérico", db_column='Ingrediente_idIngrediente')
    Cantidad = models.DecimalField(max_digits=10, decimal_places=2, default=0, db_column='Cantidad')

    class Meta:
        db_table = 'RecetaIngrediente'  # 👈 nombre exacto

    def __str__(self):
        return f"{self.Cantidad} de {self.Ingrediente_idIngrediente} en {self.Receta_idReceta}"


# -------------------- COMPROBANTE --------------------
class Comprobante(models.Model):
    IdComprobante = models.AutoField(primary_key=True, db_column='IdComprobante')
    Receta = models.CharField(max_length=100, default="Receta genérica", db_column='Receta')
    Costo_Total = models.IntegerField(default=0, db_column='Costo_Total')
    Factor_Multiplicacion = models.DecimalField(max_digits=10, decimal_places=4, default=1, db_column='Factor_Multiplicacion')
    Iva = models.DecimalField(max_digits=10, decimal_places=4, default=0.19, db_column='Iva')
    Precio_Bruto = models.IntegerField(default=0, db_column='Precio_Bruto')

    class Meta:
        db_table = 'Comprobante'  # 👈 nombre exacto

    def __str__(self):
        return f"Comprobante {self.IdComprobante} - {self.Receta}"


# -------------------- HISTORIAL --------------------
class Historial(models.Model):
    idHistorial = models.AutoField(primary_key=True, db_column='idHistorial')
    Fecha_Entrega = models.DateTimeField(blank=True, null=True, db_column='Fecha_Entrega')
    Fecha_Modificacion = models.DateTimeField(auto_now=True, db_column='Fecha_Modificacion')
    Usuario = models.CharField(max_length=100, default="Usuario genérico", db_column='Usuario')
    Receta = models.CharField(max_length=100, default="Receta genérica", db_column='Receta')
    Cambio_Realizado = models.TextField(blank=True, null=True, default="Sin cambios", db_column='Cambio_Realizado')

    class Meta:
        db_table = 'Historial'  # 👈 nombre exacto

    def __str__(self):
        return f"Historial {self.idHistorial} - Receta {self.Receta}"
