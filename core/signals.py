from django.db.models.signals import post_save, pre_delete, post_migrate
from django.dispatch import receiver
from django.db.utils import OperationalError, ProgrammingError

from .models import Receta, Historial, Rol, UnidadMedicion


# ============================================================
#   SOLO REGISTRAR CREACIÓN DE RECETAS
# ============================================================
@receiver(post_save, sender=Receta)
def registrar_creacion(sender, instance, created, **kwargs):
    """
    Registra SOLO cuando se crea una receta.
    La modificación ya no se registra aquí para evitar duplicados.
    """
    if not created:
        return  # evitar spam de historial innecesario

    usuario = getattr(instance, "Usuario", None)

    try:
        Historial.objects.create(
            Usuario=usuario,
            Receta=instance,
            Cambio_Realizado=f"Se creó la receta '{instance.Nombre_Receta}'."
        )
    except (OperationalError, ProgrammingError):
        pass


# ============================================================
#   REGISTRAR ELIMINACIÓN DE RECETAS
# ============================================================
@receiver(pre_delete, sender=Receta)
def registrar_eliminacion(sender, instance, **kwargs):
    usuario = getattr(instance, "Usuario", None)

    try:
        Historial.objects.create(
            Usuario=usuario,
            Receta=instance,
            Cambio_Realizado=f"La receta '{instance.Nombre_Receta}' fue eliminada."
        )
    except (OperationalError, ProgrammingError):
        pass


# ============================================================
#   CREAR ROLES POR DEFECTO
# ============================================================
@receiver(post_migrate)
def crear_roles_por_defecto(sender, **kwargs):
    if sender.name != "core":
        return

    try:
        roles = ["Profesor", "Alumno"]
        for nombre in roles:
            Rol.objects.get_or_create(NombreRol=nombre)

    except (OperationalError, ProgrammingError):
        pass


# ============================================================
#   CREAR UNIDADES DE MEDICIÓN POR DEFECTO
# ============================================================
@receiver(post_migrate)
def crear_unidades_por_defecto(sender, **kwargs):
    if sender.name != "core":
        return

    unidades = [
        ("Gramos", "g"),
        ("Kilogramos", "kg"),
        ("Mililitros", "ml"),
        ("Litros", "l"),
        ("Unidad", "u"),
        ("Cucharada", "cda"),
        ("Cucharadita", "cdta"),
        ("Pizca", "pz"),
    ]

    try:
        for nombre, abrev in unidades:
            UnidadMedicion.objects.get_or_create(
                Nombre_Unidad=nombre,
                Abreviatura=abrev
            )
    except (OperationalError, ProgrammingError):
        pass
