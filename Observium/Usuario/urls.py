from django.conf.urls import url
from . import views

urlpatterns = [

    url(r'^$',
        views.LoginUsuario,
        name='LoginUsuario'),

    url(r'^logout$',
        views.logout_view,
        name="logout"),

    url(r'^Modulo_Usuario$',
        views.VistaUsuario,
        name='VistaUsuario'),

    url(r'^Editar_Usuario/(?P<Id>\d+)/$',
        views.EditarUsuario,
        name='EditarUsuario'),
]
