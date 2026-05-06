from rest_framework import serializers
from .models import Psicologo, Paciente

class PsicologoSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Psicologo
        fields = ['nombres', 'dni', 'email', 'foto_url']

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if request and obj.foto_url:
            return request.build_absolute_uri(obj.foto_url)
        return obj.foto_url
    

class PacienteSerializer(serializers.ModelSerializer):
    foto_url = serializers.SerializerMethodField()

    class Meta:
        model = Paciente
        fields = ['nombres', 'dni', 'email', 'foto_url']  

    def get_foto_url(self, obj):
        request = self.context.get('request')
        if request and obj.foto_url:
            return request.build_absolute_uri(obj.foto_url)
        return obj.foto_url 
