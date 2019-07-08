from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^$', views.ProductoList, name='ProductoList'),
    url(
        r'^producto/(?P<Id_Producto>[0-9]+)/$',
        views.ProductoDetalle,
        name='ProductoDetalle'
        ),
    url(r'^Carrito/$', views.ProductoCarrito, name='ProductoCarrito'),

    url(r'^Editar_carrito/(?P<Id>\d+)/$',
        views.ProductoEditar,
        name='ProductoEditar'),

    url(r'^Eliminar_carrito/(?P<Id>\d+)/$',
        views.ProductoEliminar,
        name='ProductoEliminar'),

    url(r'^Busqueda/(?P<Id_CategoriaPadre>\d+)/$',
        views.Busqueda,
        name='Busqueda'),

]
