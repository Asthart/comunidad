from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from multiupload.fields import MultiFileField

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

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

class PublicacionForm(forms.ModelForm):
    archivos = MultiFileField(min_num=1, max_num=5, max_file_size=1920*1920*5)
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    comunidad = forms.ModelChoiceField(
        queryset=Comunidad.objects.all(),
        required=False
    )
    
    class Meta:
        model = Publicacion
        fields = ('contenido', 'tags', 'archivos', 'comunidad')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivos'].required = True