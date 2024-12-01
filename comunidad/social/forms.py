from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError
class ComunidadForm(forms.ModelForm):
    class Meta:
        model = Comunidad
        fields = ['nombre', 'descripcion', 'publica']

class SolicitudCrowuserForm(forms.ModelForm):
    class Meta:
        model = SolicitudCrowuser
        fields = ['descripcion']

class ProyectoForm(forms.ModelForm):
    class Meta:
        model = Proyecto
        fields = ['titulo', 'descripcion', 'imagenes', 'documentos']

class ArchivoProyectoForm(forms.ModelForm):
    class Meta:
        model = ArchivoProyecto
        fields = ['archivo', 'tipo', 'nombre']
        from django import forms
from django.forms import ModelForm, HiddenInput

class DesafioForm(ModelForm):
    class Meta:
        model = Desafio
        fields = ['titulo', 'descripcion','tipo_desafio', 'objetivo_monto', 'min_monto', 'max_monto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # Verificar si existe un ID primario
            if self.instance.tipo_desafio == 'donacion':
                self.fields['min_monto'].widget.attrs['readonly'] = True
                self.fields['max_monto'].widget.attrs['readonly'] = True
            else:
                self.fields['min_monto'].widget.attrs['readonly'] = True
                self.fields['max_monto'].widget.attrs['readonly'] = True



# Para crear el formulario
form = DesafioForm(instance=Desafio)

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

    def clean_username(self):
        username = self.cleaned_data.get('username')
        slug = slugify(username)
        self.cleaned_data['slug'] = slug
        return username

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
        field_classes = {
            'slug': models.SlugField,
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
        username = self.cleaned_data.get('username')
        slug = slugify(username)
        user.slug = slug
        if commit:
            user.save()
        return user

class PublicacionForm(forms.ModelForm):
    imagen = forms.ImageField(required=False)
    '''
    tags = forms.ModelMultipleChoiceField(
        queryset=Tematica.objects.all(),
        widget=forms.CheckboxSelectMultiple
    )
    '''

    class Meta:
        model = Publicacion
        fields = ('contenido','imagen')

class RespuestaForm(forms.ModelForm):
    class Meta:
        model = Respuesta
        fields = ('respuesta',)

class ComentarioForm(forms.ModelForm):
    class Meta:
        model = Comentario
        fields = ('contenido',)

class ComentarioProyectoForm(forms.ModelForm):
    class Meta:
        model = ComentarioProyecto
        fields = ('contenido',)

class DonacionComunidadForm(forms.ModelForm):
    class Meta:
        model = DonacionComunidad
        fields = ['identificador_transferencia', 'cantidad']

    widgets = {
        'cantidad': forms.NumberInput(attrs={'step': 'any'}),
    }

class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['biografia', 'puntos', 'foto_perfil']
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }

class EditUserProfilePersonalForm(forms.ModelForm):
    class Meta:
        model = PerfilUsuario
        fields = ['biografia', 'foto_perfil']
        widgets = {
            'biografia': forms.Textarea(attrs={'rows': 4}),
        }

class EditUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

class RangoFechaForm(forms.Form):
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
