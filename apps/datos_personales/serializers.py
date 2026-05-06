from rest_framework import serializers
from .models import DatosPersonales

class DatosPersonalesSerializer(serializers.ModelSerializer):
    id_std_civil = serializers.StringRelatedField()
    id_pais = serializers.StringRelatedField()
    id_provincia = serializers.StringRelatedField()
    id_localidad = serializers.StringRelatedField()
    id_zona = serializers.StringRelatedField()

    class Meta:
        model = DatosPersonales
        fields = [
            'nro_socio',
            'telefono',
            'domicilio',
            'id_std_civil',
            'id_pais',
            'id_provincia',
            'id_localidad',
            'id_zona',
        ]
