from django.db.models.signals import post_save, pre_delete, post_migrate
from django.dispatch import receiver
from .models import Receta, Historial, Rol

# -------------------- CREACIÓN / MODIFICACIÓN --------------------
@receiver(post_save, sender=Receta)
def registrar_creacion_modificacion(sender, instance, created, **kwargs):
    # ⚠️ No existe Usuario_IdUsuario en tu modelo, usamos Usuario si está, o "Desconocido"
    usuario = getattr(instance, "Usuario", "Desconocido")
    
    if created:
        cambio = f"Se creó la receta '{instance.Nombre_Receta}'."
    else:
        cambio = f"Se modificó la receta '{instance.Nombre_Receta}'."

    Historial.objects.create(
        Usuario=usuario,          # CharField en tu modelo
        Receta=instance.Nombre_Receta,  # CharField en tu modelo
        Cambio_Realizado=cambio
    )

# -------------------- BORRADO --------------------
@receiver(pre_delete, sender=Receta)
def registrar_eliminacion(sender, instance, **kwargs):
    usuario = getattr(instance, "Usuario", "Desconocido")
    nombre_receta = instance.Nombre_Receta

    Historial.objects.create(
        Usuario=usuario,                # CharField
        Receta=nombre_receta,           # CharField
        Cambio_Realizado=f"La receta '{nombre_receta}' fue eliminada."
    )

# -------------------- ROLES POR DEFECTO --------------------
@receiver(post_migrate)
def crear_roles_por_defecto(sender, **kwargs):
    if sender.name == 'core':
        roles = ['Profesor', 'Alumno']
        for nombre in roles:
            Rol.objects.get_or_create(NombreRol=nombre)
