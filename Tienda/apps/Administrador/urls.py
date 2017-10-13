from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    url(r'^$',
        views.LoginAdministrador,
        name='LoginAdministrador'),

    url(r'^logout$', auth_views.logout, {'next_page': '/Administrador/'},
        name="logout"),

    url(r'^Modulo_Administrador$',
        views.AdministradorVista,
        name='AdministradorVista'),

    url(r'^Modulo_Producto$',
        views.ProductoVista,
        name='ProductoVista'),

    url(r'^Editar_Administrador/(?P<Id>\d+)/$',
        views.AdministradorEditar,
        name='AdministradorEditar'),

    url(r'^Eliminar_Administrador/(?P<Id>\d+)/$',
        views.AdministradorEliminar,
        name='AdministradorEliminar'),

    url(r'^Editar_Producto/(?P<Id>\d+)/$',
        views.ProductoEditar,
        name='ProductoEditar'),

    url(r'^Eliminar_Producto/(?P<Id>\d+)/$',
        views.ProductoEliminar,
        name='ProductoEliminar'),

    url(r'^Modulo_Categoria$',
        views.CategoriaVista,
        name='CategoriaVista'),

    url(r'^Editar_Categoria/(?P<Id>\d+)/$',
        views.CategoriaEditar,
        name='CategoriaEditar'),

    url(r'^Eliminar_Categoria/(?P<Id>\d+)/$',
        views.CategoriaEliminar,
        name='CategoriaEliminar'),

    url(r'^Editar_CategoriaPadre/(?P<Id>\d+)/$',
        views.CategoriaPadreEditar,
        name='CategoriaPadreEditar'),

    url(r'^Eliminar_CategoriaPadre/(?P<Id>\d+)/$',
        views.CategoriaPadreEliminar,
        name='CategoriaPadreEliminar'),

    url(r'^Modulo_MetodoDePago$',
        views.MetodoDePagoVista,
        name='MetodoDePagoVista'),

    url(r'^Editar_MetodoDePago/(?P<Id>\d+)/$',
        views.MetodoDePagoEditar,
        name='MetodoDePagoEditar'),

    url(r'^Eliminar_MetodoDePago/(?P<Id>\d+)/$',
        views.MetodoDePagoEliminar,
        name='MetodoDePagoEliminar'),

    url(r'^Registrar$',
        views.Registrar,
        name='Registrar'),

]
