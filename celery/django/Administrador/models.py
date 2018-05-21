from django.db import models
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField


class Administrador(models.Model):
    Administrador = models.OneToOneField(User, on_delete=models.CASCADE)
    Descripcion = models.CharField(max_length=120)
    Telefono = models.IntegerField()
    Imagen = ImageField(upload_to='Administradores')

    def __str__(self):
        return '{}'.format(
            self.Administrador)

    class Meta:
        verbose_name = 'Administrador'
        verbose_name_plural = 'Administradores'
