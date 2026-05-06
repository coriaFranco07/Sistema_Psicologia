from rest_framework import serializers
from .models import Usuario

class UsuarioSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Usuario
        fields = ['username', 'nombres', 'dni', 'email', 'foto_url']

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if request and obj.foto_url:
            return request.build_absolute_uri(obj.foto_url)
        return obj.foto_url
