from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('platillos/', views.platillos_list, name='platillos'),
    path('platillo/<int:pk>/', views.platillo_detail, name='platillo_detail'),
    path('platillo/<int:pk>/eliminar/', views.eliminar_platillo, name='eliminar_platillo'),
    path('agregar/', views.agregar_platillo, name='agregar_platillo'),
    path('calculadora/', views.calculadora, name='calculadora'),
    path('perfil/', views.perfil, name='perfil'),
    path("costos/", views.costos_view, name="costos"),
    path("ingredientes/", views.ingredientes_view, name="ingredientes"),

]