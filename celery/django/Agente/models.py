from django.db import models
from django.contrib.auth.models import User

tipos = (
    (1, 'v1'),
    (2, 'v2c'),
    (3, 'v3')
)


class Agente(models.Model):
    NombreHost = models.CharField(max_length=120)
    Ip = models.CharField(max_length=120)
    Ip_publica = models.CharField(max_length=120)
    Protocolo = models.PositiveIntegerField(choices=tipos)
    Puerto = models.IntegerField()
    Comunidad = models.CharField(max_length=120)
    Administrador_Agente = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE)

    def __str__(self):
        return '{} {}'.format(
            self.NombreHost,
            self.Comunidad)

    class Meta:
        verbose_name = 'Agente'
        verbose_name_plural = 'Agentes'
