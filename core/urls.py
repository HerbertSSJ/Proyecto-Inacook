from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import perfil_view, CambiarContraseñaView

urlpatterns = [
    # --- Autenticación ---
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # --- Dashboard principal ---
    path("dashboard/", views.dashboard, name="dashboard"),

    # --- Gestión de recetas ---
    path("subir-receta/", views.subir_receta, name="subir_receta"),
    path("ver-recetas/", views.ver_recetas, name="ver_recetas"),
    path("editar-receta/<int:idReceta>/", views.editar_receta, name="editar_receta"),
    path("borrar-receta/<int:idReceta>/", views.borrar_receta, name="borrar_receta"),

    # --- Perfil y contraseña ---
    path("perfil/", perfil_view, name="perfil"),
    path("cambiar-contraseña/", CambiarContraseñaView.as_view(), name="cambiar_contraseña"),

    # --- Otras funciones ---
    path("calculadora/", views.calculadora_view, name="calculadora"),
    path("historial/", views.ver_historial, name="ver_historial"),

    #----comprobante-------
    path("comprobante/<int:idReceta>/", views.comprobante_receta, name="comprobante_receta"),

    # --- Gestión de ingredientes y unidades ---
    path("crear-ingrediente/", views.crear_ingrediente, name="crear_ingrediente"),
    path("ingredientes/", views.ver_ingredientes, name="ver_ingredientes"),

    # --- Vista del profesor ---
    path("recetas/alumnos/", views.ver_recetas_alumnos, name="ver_recetas_alumnos"),
]

# Configuración para archivos multimedia (imágenes)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
