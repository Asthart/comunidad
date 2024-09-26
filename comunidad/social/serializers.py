from rest_framework import serializers
from django.contrib.auth.models import User
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ComunidadSerializer(serializers.ModelSerializer):
    miembros = UserSerializer(many=True, read_only=True)
    
    class Meta:
        model = Comunidad
        fields = '__all__'

class ProyectoSerializer(serializers.ModelSerializer):
    creador = UserSerializer(read_only=True)
    
    class Meta:
        model = Proyecto
        fields = '__all__'

class DesafioSerializer(serializers.ModelSerializer):
    creador = UserSerializer(read_only=True)
    
    class Meta:
        model = Desafio
        fields = '__all__'

class ArchivoProyectoSerializer(serializers.ModelSerializer):
    tipo_display = serializers.CharField(source='get_tipo_display')
    
    class Meta:
        model = ArchivoProyecto
        fields = ['archivo', 'tipo_display', 'nombre', 'subido_por', 'fecha_subida']