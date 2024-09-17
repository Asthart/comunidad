from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comunidades_administradas')
    miembros = models.ManyToManyField(User, related_name='comunidades')
    def __str__(self):
        return self.nombre

class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagenes = models.ImageField(upload_to='imagenes_proyecto/', blank=True, null=True)
    videos = models.FileField(upload_to='videos_proyecto/', blank=True, null=True)
    documentos = models.FileField(upload_to='documentos_proyecto/', blank=True, null=True)
    archivos = models.ManyToManyField('ArchivoProyecto', related_name='proyectos', blank=True)
    def __str__(self):
        return self.titulo

class ArchivoProyecto(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('video', 'Video'),
        ('documento', 'Documento'),
    ]
    archivo = models.FileField(upload_to='archivos_proyecto/')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=255)
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
    
class Desafio(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    def __str__(self):
        return self.titulo

'''class Rol(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    permisos = models.ManyToManyField(Permission)

    def __str__(self):
        return self.nombre'''

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    biografia = models.TextField(blank=True)
    #rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return self.usuario.username

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfilusuario.save()

class ActividadUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    tipo_actividad = models.CharField(max_length=50)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    puntos_ganados = models.IntegerField(default=0)
    def __str__(self):
        return f'{self.usuario.username} - {self.tipo_actividad}'
    
class MensajeChat(models.Model):
    emisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_enviados')
    receptor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_recibidos')
    contenido = models.TextField()
    fecha_hora = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)

    class Meta:
        ordering = ['fecha_hora']

    def __str__(self):
        return f'{self.emisor.username} to {self.receptor.username}: {self.contenido[:20]}'