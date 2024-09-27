from arrow import now
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.utils import timezone
from multiupload.fields import MultiFileField

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comunidades_administradas')
    miembros = models.ManyToManyField(User, related_name='comunidades')
    activada = models.BooleanField(default=False)
    publica = models.BooleanField(default=False)
    
    def __str__(self):
        return self.nombre
    @property
    def publicaciones(self):
        return Publicacion.objects.filter(comunidad=self).order_by('-fecha_publicacion')

class Proyecto(models.Model): # quiero hacerle a este lo mismo que le hice a los archivos de las publicaciones
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
    TIPOS_DESAFIO = (
        ('donacion', 'Donación'),
        ('votacion', 'Votación'),
    )
    
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey('Comunidad', on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    tipo_desafio = models.CharField(max_length=10, choices=TIPOS_DESAFIO, default='donacion')
    min_donaciones = models.IntegerField(null=True, blank=True)
    max_donaciones = models.IntegerField(null=True, blank=True)
    proyecto = models.URLField(null=True, blank=True)
    votos_positivos = models.IntegerField(default=0)
    votos_negativos = models.IntegerField(default=0)
    def __str__(self):
        return self.titulo
    @classmethod
    def verificar_min_max_donaciones(cls):
        for desafio in cls.objects.all():
            if desafio.tipo_desafio == 'donacion':
                donaciones = Donacion.objects.filter(desafio=desafio)
                if len(donaciones) < desafio.min_donaciones:
                    raise ValueError(f"El desafío '{desafio.titulo}' requiere al menos {desafio.min_donaciones} donaciones.")
                elif len(donaciones) > desafio.max_donaciones:
                    raise ValueError(f"El desafío '{desafio.titulo}' solo permite hasta {desafio.max_donaciones} donaciones.")

    @classmethod
    def actualizar_votos(cls):
        for desafio in cls.objects.all():
            if desafio.tipo_desafio == 'votacion':
                votos = Voto.objects.filter(desafio=desafio)
                desafio.votos_positivos = votos.filter(es_positivo=True).count()
                desafio.votos_negativos = votos.filter(es_positivo=False).count()

class Donacion(models.Model):
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, related_name='donaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

class Voto(models.Model):
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    es_positivo = models.BooleanField(default=False)

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    biografia = models.TextField(blank=True)
    #rol = models.ForeignKey(Rol, on_delete=models.SET_NULL, null=True)
    puntos = models.IntegerField(default=0)
    seguidos = models.ManyToManyField('self', symmetrical=False, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil', blank=True, null=True)

    def sigue_a(self, usuario):
        perfil_usuario = PerfilUsuario.objects.get(usuario=usuario)
        print(f"Verificando si {self.usuario.username} sigue a {perfil_usuario.usuario.username}")
        sigue = perfil_usuario.seguidos.filter(id=self.usuario.id).exists()
        print(f"Resultado: {sigue}")
        return sigue
    def seguir_usuario(self, usuario_a_seguir):
        perfil_usuario_a_seguir = PerfilUsuario.objects.get(usuario=usuario_a_seguir)
        self.seguidos.add(perfil_usuario_a_seguir)

    def dejar_de_seguir_usuario(self, usuario_a_dejar_de_seguir):
        perfil_usuario_a_dejar_de_seguir = PerfilUsuario.objects.get(usuario=usuario_a_dejar_de_seguir)
        self.seguidos.remove(perfil_usuario_a_dejar_de_seguir)
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
    room_name = models.CharField(max_length=255)
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido = models.BooleanField(default=False)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.emisor.username} en {self.room_name}: {self.contenido[:20]}'

    def marcar_como_leido(self):
        if not self.leido:
            self.leido = True
            self.fecha_lectura = timezone.now()
            self.save()

class Publicacion(models.Model):
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')
    archivos = MultiFileField(min_num=1, max_num=5)
    comunidad = models.ForeignKey('Comunidad', on_delete=models.SET_NULL, null=True, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Publicación de {self.autor.username} en {self.fecha_publicacion}"
    
class Tag(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    
class PublicacionVista(models.Model):
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_vista = models.DateTimeField(auto_now_add=True)
    
from django.db import models

class TerminosCondiciones(models.Model):
    texto = models.TextField()
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Términos y Condiciones"
    
class Clasificacion(models.Model):
    nombre = models.CharField(max_length=50)
    umbral_puntos = models.IntegerField()
    print(f"Verificando si {nombre} tiene {umbral_puntos}")
    def __str__(self):
        return self.nombre
    
class Adjunto(models.Model):
    archivo = models.FileField(upload_to='publicaciones/archivos/')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='adjuntos')
    
class Action(models.Model):
    name = models.CharField(max_length=100)
    points = models.IntegerField(default=0)

class UserAction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    

class Premio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.nombre}"

class Concurso(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    premio = models.ForeignKey(Premio, on_delete=models.CASCADE)

class ResultadoConcurso(models.Model):
    concurso = models.ForeignKey(Concurso, on_delete=models.CASCADE)
    ganador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_resultado = models.DateField()
    
class Campaign(models.Model):
    activa = models.BooleanField(default=True)
    desafio = models.OneToOneField(Desafio, on_delete=models.CASCADE)

    def __str__(self):
        return self.desafio.titulo
    
    @property
    def respuestas(self):
        return Respuesta.objects.filter(campaign=self).order_by('-fecha')
    
class Respuesta(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)
    puntuacion = models.IntegerField(default=0)
    
    def __str__(self):
        return self.respuesta
    
    @property
    def estrellas(self):
        return range(self.puntuacion)

class AdjuntoRespuesta(models.Model):
    archivo = models.FileField(upload_to='respuestas/archivos/')
    respuesta = models.ForeignKey(Respuesta, on_delete=models.CASCADE, related_name='adjuntos')
    