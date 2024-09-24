from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

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
    username = forms.CharField(label='Nombre de usuario', max_length=30, required=True)
    first_name = forms.CharField(label='Nombres', max_length=30, required=True)
    last_name = forms.CharField(label='Apellidos', max_length=30, required=True)
    email = forms.EmailField(label='Correo electrónico', required=True)
    
    password1 = forms.CharField(label='Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Minimo 8 caracteres'}))
    password2 = forms.CharField(label='Confirmar Contraseña', widget=forms.PasswordInput(attrs={'placeholder': 'Repite la contraseña'}))

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Las contraseñas no coinciden.")
        
        return password2

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe contener al menos 8 caracteres.")
        
        if password.isdigit():
            raise ValidationError("La contraseña no puede ser completamente numérica.")
        
        if password.lower() in ['123456', 'qwerty']:
            raise ValidationError("La contraseña no puede ser una clave utilizada comúnmente.")
        
        if password.lower() == password.upper():
            raise ValidationError("La contraseña no puede asemejarse tanto a su otra información personal.")
        
        return password

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