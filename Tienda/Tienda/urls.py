from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^Administrador/', include('Administrador.urls',
                                    namespace='Administrador')),
    url(r'^Producto/', include('Producto.urls',
                               namespace='Producto')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
