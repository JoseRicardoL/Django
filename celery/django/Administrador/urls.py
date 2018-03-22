from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^$', views.LoginAdministrador, name='LoginAdministrador'),

    url(r'^logout$', views.logout_view, name="logout"),

    url(r'^VistaAdministrador$', views.VistaAdministrador,
        name='VistaAdministrador'),

    url(r'^Editar_Administrador/(?P<Id>\d+)/$', views.EditarAdministrador,
        name='EditarAdministrador'),

    url(r'^Registrar$', views.Registrar, name='Registrar'),

    url(r'^Contrato$', views.Contrato, name='Contrato'),

    url(r'^MasDatos$', views.MasDatos, name='MasDatos'),
]
