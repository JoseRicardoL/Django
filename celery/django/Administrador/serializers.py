from rest_framework import serializers
from .models import Administrador


class AdministradorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Administrador
        fields = ('id', 'Descripcion', 'Telefono',
                  'Imagen', 'Administrador_id')
