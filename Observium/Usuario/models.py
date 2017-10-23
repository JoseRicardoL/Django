# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from sorl.thumbnail import ImageField


class Usuario(models.Model):
    Usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    Descripcion = models.CharField(max_length=120)
    Telefono = models.IntegerField()
    Imagen = ImageField(upload_to='Usuarios')

    def __str__(self):
        return '{}'.format(
            self.Usuario)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
