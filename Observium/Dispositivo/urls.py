from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^Modulo_Dispositivo$',
        views.VistaDispositivo,
        name='VistaDispositivo'),

    url(r'^Agregar_Dispositivo$',
        views.AgregarDispositivo,
        name='AgregarDispositivo'),

    url(r'^Editar_Dispositivo/(?P<Id>\d+)/$',
        views.EditarDispositivo,
        name='EditarDispositivo'),

    url(r'^Eliminar_Dispositivo/(?P<Id>\d+)/$',
        views.EliminarDispositivo,
        name='EliminarDispositivo'),

    url(r'^Individual_Dispositivo/(?P<Id>\d+)/$',
        views.IndividualDispositivo,
        name='IndividualDispositivo'),
]
