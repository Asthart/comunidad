import uuid
from arrow import now
from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.utils import timezone
from multiupload.fields import MultiFileField
from django.template.defaultfilters import slugify
from django.db import models
from django.contrib.auth.models import User
class Premio(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    tipo = models.CharField(max_length=50)
    def __str__(self):
        return f"{self.nombre}"

class Tematica(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre

class Comunidad(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    administrador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comunidades_administradas')
    miembros = models.ManyToManyField(User, related_name='comunidades')
    activada = models.BooleanField(default=False)
    publica = models.BooleanField(default=False)
    #donaciones = models.BooleanField(default=False)
    foto_perfil = models.ImageField(upload_to='comunidades/perfiles/', null=True, blank=True, default='comunidades/perfiles/perfil_default.jpg')
    banner = models.ImageField(upload_to='comunidades/banners/', null=True, blank=True,default='comunidades/banners/banner_default.jpg')
    tematica = models.ManyToManyField(Tematica,related_name='Tema',blank=True,null=True)
    slug = models.SlugField(default="", null=False)
    acepta_donaciones=models.BooleanField(default=False)

    class Meta:
       verbose_name = 'Comunidad'
       verbose_name_plural = 'Comunidades'

    def __str__(self):
        return self.nombre

    @property
    def publicaciones(self):
        return Publicacion.objects.filter(comunidad=self).order_by('-fecha_publicacion')
    def es_miembro(self, usuario):
        return self.miembros.filter(id=usuario.id).exists()


    def cant_miembros(self):
        return self.miembros.count()

    def unirse(self, usuario):
        self.miembros.add(usuario)
        return self.miembros.filter(id=usuario.id).exists()

    def salir(self, usuario):
        self.miembros.remove(usuario)
        return self.miembros.filter(id=usuario.id).exists()

    @property
    def proyectos(self):
        return Proyecto.objects.filter(comunidad=self)


class Crowuser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Proyecto(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    imagenes = models.ImageField(upload_to='comunidades/imagenes_proyecto/', blank=True,default="")
    documentos = models.FileField(upload_to='comunidades/documentos_proyecto/', blank=True,default="")
    slug = models.SlugField(default="", null=False)
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.titulo

    def comentarios(self):
        return ComentarioProyecto.objects.filter(proyecto=self).order_by('-fecha_comentarios')

class ComentarioProyecto(models.Model):
    proyecto = models.ForeignKey(Proyecto, related_name='comentarios', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.proyecto}"

class ArchivoProyecto(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Imagen'),
        ('documento', 'Documento'),
    ]
    archivo = models.FileField(upload_to='archivos_proyecto/')
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    nombre = models.CharField(max_length=255)
    subido_por = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre
from django.contrib.auth.models import User
from django.utils.timezone import now

class Desafio(models.Model):
    TIPOS_DESAFIO = (
        ('votacion', 'Votación'),
        ('donacion', 'Donación'),
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(max_length=250)
    creador = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField(default=now)
    fecha_fin = models.DateTimeField(null=True, blank=True)
    tipo_desafio = models.CharField(max_length=10, choices=TIPOS_DESAFIO, default='donacion')
    objetivo_monto = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    min_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0)
    max_monto = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,default=0)
    cantidad_donada = models.DecimalField(max_digits=10, decimal_places=2, null=True,default=0)
    premio = models.ForeignKey(Premio, on_delete=models.CASCADE,default=None, null=True, blank=True)
    likes = models.ManyToManyField(User, related_name='likes_desafios', blank=True)
    slug = models.SlugField(default="", null=False)
    activada = models.BooleanField(default=False)

    def total_likes(self):
        return self.likes.count()
    def __str__(self):
        return self.titulo

    @property
    def tipo(self):
        return self.tipo_desafio

    @property
    def tcampaign(self):
        return Campaña.objects.get(desafio=self)

    @classmethod
    def verificar_min_max_donaciones(cls):
        for desafio in cls.objects.all():
            if desafio.tipo_desafio == 'donacion':
                min_monto = desafio.min_monto or 0
                max_monto = desafio.max_monto or float('inf')

                donaciones = Donacion.objects.filter(desafio=desafio)
                total_donado = sum(d.monto for d in donaciones)

                if total_donado < min_monto:
                    raise ValueError(f"El desafío '{desafio.titulo}' requiere al menos {min_monto}€.")
                elif total_donado > max_monto:
                    raise ValueError(f"El desafío '{desafio.titulo}' solo permite hasta {max_monto}€.")

    @classmethod
    def actualizar_votos(cls):
        for desafio in cls.objects.all():
            if desafio.tipo_desafio == 'votacion':
                votos = Voto.objects.filter(desafio=desafio)
                desafio.votos_positivos = votos.filter(es_positivo=True).count()
                desafio.votos_negativos = votos.filter(es_positivo=False).count()

    @property
    def campaign(self):
        return Campaña.objects.get(desafio=self)


class Donacion(models.Model):
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, related_name='donaciones')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)

class DonacionComunidad(models.Model):
    donador = models.ForeignKey(User, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Desafio, on_delete=models.CASCADE, null=True)
    identificador_transferencia = models.CharField(max_length=50)
    cantidad = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Donación de {self.donador.first_name} {self.donador.last_name}"
    class Meta:
       verbose_name = 'Donaciones Comunidad'
       verbose_name_plural = 'Donaciones Comunidad'
class Voto(models.Model):
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, related_name='votos')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    puntuacion = models.IntegerField(default=0)

class PerfilUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    biografia = models.TextField(blank=True)
    puntos = models.IntegerField(default=0)
    seguidos = models.ManyToManyField('self', symmetrical=False, blank=True)
    foto_perfil = models.ImageField(upload_to='fotos_perfil', blank=True, null=True, default='/fotos_perfil/default-avatar.svg')
    slug = models.SlugField(unique=True)
    no_me_gusta= models.ManyToManyField(Tematica)

    def sigue_a(self, usuario):
        perfil_usuario = PerfilUsuario.objects.get(usuario=usuario)
        print(f"Verificando si {self.usuario.username} sigue a {perfil_usuario.usuario.username}")
        sigue = perfil_usuario.seguidos.filter(id=self.usuario.id).exists()
        print(f"Resultado: {sigue}")
        return sigue
    def es_administrador_comunidad(usuario):
        return usuario.groups.filter(name='Administrador de Comunidad').exists()


    def seguir_usuario(self, usuario_a_seguir):
        perfil_usuario_a_seguir = PerfilUsuario.objects.get(usuario=usuario_a_seguir)
        self.seguidos.add(perfil_usuario_a_seguir)

    def no_gusta(self, tematica):
        self.no_me_gusta.add(tematica)

    def dejar_de_seguir_usuario(self, usuario_a_dejar_de_seguir):
        perfil_usuario_a_dejar_de_seguir = PerfilUsuario.objects.get(usuario=usuario_a_dejar_de_seguir)
        self.seguidos.remove(perfil_usuario_a_dejar_de_seguir)

    def __str__(self):
        return self.usuario.username
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.usuario.username)
        super().save(*args, **kwargs)

@receiver(post_save, sender=User)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        PerfilUsuario.objects.create(usuario=instance)

@receiver(post_save, sender=User)
def guardar_perfil_usuario(sender, instance, **kwargs):
    instance.perfilusuario.save()


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
    class Meta:
       verbose_name = 'Mensaje Chat'
       verbose_name_plural = 'Mensajes Chat'

class Publicacion(models.Model):
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    imagen = models.ImageField(blank=True, null=True, upload_to='publicaciones/imagenes/')
    #archivos = MultiFileField(min_num=1, max_num=5)
    comunidad = models.ForeignKey('Comunidad', on_delete=models.CASCADE, null=True, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    tematica = models.ForeignKey(Tematica, on_delete=models.CASCADE, null=True)

    def likes(self):
        return Like.objects.filter(publicacion=self).count()

    def like(self):
        like = Like(publicacion=self, autor=self.autor, fecha_like=timezone.now())
        like.save()
        return self.likes

    def comentarios(self):
        return Comentario.objects.filter(publicacion=self).order_by('-fecha_comentarios')

    def __str__(self):
        return f"Publicación de {self.autor.username} en {self.fecha_publicacion}"
    class Meta:
       verbose_name = 'Publicacion'
       verbose_name_plural = 'Publicaciones'

class Like(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_like = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like de {self.autor.username} en {self.publicacion}"

class Comentario(models.Model):
    publicacion = models.ForeignKey(Publicacion, related_name='comentarios', on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_comentario = models.DateTimeField(auto_now_add=True)

    def likes(self):
        return Like_Comentario.objects.filter(comentario=self).count()

    def like(self):
        like = Like_Comentario(comentario=self, autor=self.autor, fecha_like=timezone.now())
        like.save()
        return self.likes

    def __str__(self):
        return f"Comentario de {self.autor.username} en {self.publicacion}"

class Like_Comentario(models.Model):
    comentario = models.ForeignKey(Comentario, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_like = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Like de {self.autor.username} en {self.comentario}"


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
    class Meta:
        verbose_name = 'Terminos Condiciones'
        verbose_name_plural = 'Terminos Condiciones'

class TerminosCondicionesUsuario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    aceptado_en = models.DateTimeField(auto_now_add=True)
    terminos = models.ForeignKey(TerminosCondiciones, on_delete=models.CASCADE)

    @property
    def aceptado(self):
        aceptado = True
        if self.aceptado_en < self.terminos.actualizado_en:
            aceptado = False
        return aceptado


class Clasificacion(models.Model):
    nombre = models.CharField(max_length=50)
    umbral_puntos = models.IntegerField()
    print(f"Verificando si {nombre} tiene {umbral_puntos}")
    def __str__(self):
        return self.nombre
    class Meta:
         verbose_name = 'Clasificacion'
         verbose_name_plural = 'Clasificaciones'
class Adjunto(models.Model):
    archivo = models.FileField(upload_to='publicaciones/archivos/')
    publicacion = models.ForeignKey(Publicacion, on_delete=models.CASCADE, related_name='adjuntos')

class Accion(models.Model):
    nombre = models.CharField(max_length=100)
    puntos = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre
    class Meta:
        verbose_name = 'Accion'
        verbose_name_plural = 'Acciones'
class AccionUsuario(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accion = models.ForeignKey(Accion, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    puntos=models.IntegerField(default=0)

    def __str__(self):
        return self.accion.nombre

class Concurso(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    premio = models.ForeignKey(Premio, on_delete=models.CASCADE)
    ganador = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='ganador')
    documento = models.FileField(upload_to='concursos/documentos/', blank=True,default="")

    @classmethod
    def ultimo_concurso(cls):
        return cls.objects.order_by('-fecha_inicio').first()

    def tiempo_restante(self):
        ahora = timezone.now().date()
        if ahora > self.fecha_fin:
            return "Concurso finalizado"
        elif ahora < self.fecha_inicio:
            return "Concurso aún no ha comenzado"
        else:
            dias_restantes = (self.fecha_fin - ahora).days
            return f"{dias_restantes} días restantes"

class ResultadoConcurso(models.Model):
    concurso = models.ForeignKey(Concurso, on_delete=models.CASCADE)
    ganador = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_resultado = models.DateField()

class Campaña(models.Model):
    activa = models.BooleanField(default=True)
    desafio = models.OneToOneField(Desafio, on_delete=models.CASCADE)
    slug = models.SlugField(default="")

    def __str__(self):
        return self.desafio.titulo


    def generate_slug(self):
        return slugify(f"{self.desafio.titulo}-{self.id}")

    @property
    def nombre(self):
        return self.desafio.titulo

    @property
    def tipo(self):
        return self.desafio.tipo

    @property
    def respuestas(self):
        return Respuesta.objects.filter(campaign=self).order_by('-fecha').reverse()

    @property
    def comunidad(self):
        return self.desafio.comunidad

class Respuesta(models.Model):
    campaign = models.ForeignKey(Campaña, on_delete=models.CASCADE)
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    respuesta = models.CharField(max_length=300)
    fecha = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='likes', blank=True)


    def __str__(self):
        return self.respuesta

    @property
    def likes_total(self):
        return self.likes.count()

class AdjuntoRespuesta(models.Model):
    archivo = models.FileField(upload_to='respuestas/archivos/')
    respuesta = models.ForeignKey(Respuesta, on_delete=models.CASCADE, related_name='adjuntos')


class MensajeChatComunidad(models.Model):
    emisor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mensajes_comunidad_enviados')
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, related_name='mensajes')
    contenido = models.TextField()
    fecha_envio = models.DateTimeField(default=timezone.now)
    leido_por = models.ManyToManyField(User, related_name='mensajes_comunidad_leidos', blank=True)

    def __str__(self):
        return f'{self.emisor.username} en {self.comunidad.nombre}: {self.contenido[:20]}'

    def marcar_como_leido(self, usuario):
        self.leido_por.add(usuario)
        self.save()
    class Meta:
       verbose_name = 'Mensaje Chat Comunidad'
       verbose_name_plural = 'Mensajes Chat Comunidad'
class Cuenta(models.Model):
    qr_code = models.ImageField(upload_to='comunidades/qr_codes/', null=True, blank=True)
    numero_cuenta = models.CharField(max_length=100, null=True, blank=True)


class SolicitudMembresia(models.Model):
    comunidad = models.ForeignKey('Comunidad', on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=10, choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente')

    def __str__(self):
        return f"{self.usuario.username} - {self.comunidad.nombre} ({self.estado})"

class SolicitudCrowuser(models.Model):
    descripcion = models.TextField(default="")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.descripcion}"
    class Meta:
       verbose_name = 'Solicitud Crowdsourcer'
       verbose_name_plural = 'Solicitudes Crowdsourcer'

class PuntajeDesafio(models.Model):
    desafio = models.ForeignKey(Desafio, on_delete=models.CASCADE, related_name='puntajes')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    puntaje = models.PositiveIntegerField()  # Asume que el puntaje es un entero positivo (1 a 5)
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha en la que se dio el puntaje

    class Meta:
        unique_together = ('desafio', 'usuario')  # Evita que el mismo usuario puntúe más de una vez

    def __str__(self):
        return f"{self.usuario} - {self.puntaje} estrellas para {self.desafio}"

class FirstVisit(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
