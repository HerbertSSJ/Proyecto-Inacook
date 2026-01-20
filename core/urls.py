from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth.views import PasswordChangeView

urlpatterns = [
    # --- Ingredientes ---
    path("ingredientes/", views.ver_ingredientes, name="ver_ingredientes"),
    path("ingredientes/crear/", views.crear_ingrediente, name="crear_ingrediente"),
    path("ingredientes/editar/<int:id>/", views.editar_ingrediente, name="editar_ingrediente"),
    path("ingredientes/eliminar/<int:id>/", views.eliminar_ingrediente, name="eliminar_ingrediente"),


    # --- Autenticación ---
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("logout/", auth_views.LogoutView.as_view(next_page="home"), name="logout"),

    # --- Dashboard ---
    path("dashboard/", views.dashboard, name="dashboard"),

    # --- Recetas ---
    path("subir-receta/", views.subir_receta, name="subir_receta"),
    path("ver-recetas/", views.ver_recetas, name="ver_recetas"),
    path("editar-receta/<int:idReceta>/", views.editar_receta, name="editar_receta"),
    path("borrar-receta/<int:idReceta>/", views.borrar_receta, name="borrar_receta"),

    # --- Perfil ---
    path("perfil/", views.perfil_view, name="perfil"),
    path("cambiar-contraseña/", PasswordChangeView.as_view(template_name="cambiar_contraseña.html"), name="cambiar_contraseña"),

    # --- Calculadora / Historial ---
    path("calculadora/", views.calculadora_view, name="calculadora"),
    path("historial/", views.ver_historial, name="ver_historial"),

    # --- Comprobante ---
    path("comprobante/<int:idReceta>/", views.comprobante_receta, name="comprobante_receta"),

    # --- Profesor ---
    path("recetas/alumnos/", views.ver_recetas_alumnos, name="ver_recetas_alumnos"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
