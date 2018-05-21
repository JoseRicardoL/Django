from rest_framework import serializers
from .models import Agente


class AgenteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agente
        fields = ('id', 'NombreHost', 'Ip', 'Ip_publica', 'Protocolo',
                  'Puerto', 'Comunidad', 'Administrador_Agente_id')
