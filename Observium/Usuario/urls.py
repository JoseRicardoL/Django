from django.conf.urls import url
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

    url(r'^$',
        views.LoginUsuario,
        name='LoginUsuario'),

    url(r'^logout$', auth_views.logout, {'next_page': '/'},
        name="logout"),

    url(r'^Modulo_Usuario$',
        views.VistaUsuario,
        name='VistaUsuario'),

    url(r'^Editar_Usuario/(?P<Id>\d+)/$',
        views.EditarUsuario,
        name='EditarUsuario'),
]
