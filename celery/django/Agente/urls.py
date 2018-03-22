from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^Modulo_Agente$', views.VistaAgente, name='VistaAgente'),

    url(r'^Agregar_Agente$', views.AgregarAgente, name='AgregarAgente'),

    url(r'^Editar_Agente/(?P<Id>\d+)/$', views.EditarAgente,
        name='EditarAgente'),

    url(r'^Eliminar_Agente/(?P<Id>\d+)/$', views.EliminarAgente,
        name='EliminarAgente'),

    url(r'^Individual_Agente/(?P<Id>\d+)/$', views.IndividualAgente,
        name='IndividualAgente'),

]
