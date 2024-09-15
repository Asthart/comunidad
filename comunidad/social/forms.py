from django import forms
from .models import Comunidad, Proyecto, Desafio, ArchivoProyecto

class ComunidadForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ['nombre', 'descripcion']

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'comunidad', 'imagenes', 'videos', 'documentos']

class ArchivoProyectoForm(forms.ModelForm):
    class Meta:
        model = ArchivoProyecto
        fields = ['archivo', 'tipo', 'nombre']
class DesafioForm(forms.ModelForm):
    class Meta:
        model = Desafio
        fields = ['titulo', 'descripcion', 'comunidad', 'fecha_inicio', 'fecha_fin']