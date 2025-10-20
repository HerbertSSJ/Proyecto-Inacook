from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import perfil_view, CambiarContraseñaView

urlpatterns = [
    path("", views.home, name="home"),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('subir-receta/', views.subir_receta, name='subir_receta'),
    path("ver-recetas/", views.ver_recetas, name="ver_recetas"),
    path('comprobante/<int:idReceta>/', views.comprobante_receta, name='comprobante_receta'),
    path('perfil/', perfil_view, name='perfil'),
    path('cambiar-contraseña/', CambiarContraseñaView.as_view(), name='cambiar_contraseña'),
    path('calculadora/', views.calculadora_view, name='calculadora'),
    path('historial/', views.ver_historial, name='ver_historial'),
    path("editar-receta/<int:idReceta>/", views.editar_receta, name="editar_receta"),
    path("borrar-receta/<int:idReceta>/", views.borrar_receta, name="borrar_receta"),
    path("crear-ingrediente/", views.crear_ingrediente, name="crear_ingrediente"),
    path('ingredientes/', views.ver_ingredientes, name='ver_ingredientes'),
    path("crear-unidad-medicion/", views.crear_unidad_medicion, name="crear_unidad_medicion"),
    path('recetas/alumnos/', views.ver_recetas_alumnos, name='ver_recetas_alumnos'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)