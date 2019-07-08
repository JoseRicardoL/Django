from django.db import models
from django.contrib.auth.models import User


class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Direccion = models.CharField(max_length=120)
    Telefono = models.IntegerField()
    Imagen = models.ImageField(blank=True)

    def __str__(self):
        return '{} '.format(
            self.user.username)

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'


class Cliente(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    Direccion = models.CharField(max_length=120)
    Telefono = models.IntegerField()
    Imagen = models.ImageField(blank=True)

    def __str__(self):
        return '{} {}'.format(
            self.user.username,
            self.Tipo,)

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
