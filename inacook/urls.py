"""
URL configuration for Inacook project.

El archivo define las rutas principales del proyecto y conecta
las URLs de la aplicación 'core' donde se encuentra toda la lógica.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # --- Panel de administración ---
    path("admin/", admin.site.urls),

    # --- URLs principales del proyecto (app 'core') ---
    path("", include("core.urls")),
]

# --- Configuración de archivos multimedia (imágenes, etc.) ---
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
