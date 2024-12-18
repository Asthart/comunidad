# views.py
from datetime import datetime, timedelta
from decimal import Decimal
import os
from pyexpat.errors import messages
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.db.models import Q,Sum,Avg
import requests
from .models import *
from .forms import *
from .utils import update_user_points, get_clasificacion, is_first_visit
from django.core.mail import send_mail
from django.views.generic import ListView
from django.urls import path
from .decorators import *

@requires_login_or_404
@login_required
def inicio(request):
    terminos = TerminosCondiciones.objects.all().first()
    is_superuser = request.user.is_superuser
    user = request.user
    profile = PerfilUsuario.objects.get(usuario=user)
    no_me_gustan = [no.id for no in profile.no_me_gusta.all()]

    if terminos == None:
        return render(request, 'base.html', {'is_superuser': is_superuser})

    profile = PerfilUsuario.objects.get(usuario=user)
    contador = Concurso.ultimo_concurso()
    # Obtener las comunidades del usuario
    comunidades = Comunidad.objects.filter(miembros=user, activada=True)
    temas_comunidades = Tematica.objects.filter(Tema__in=comunidades)
    comunidades_relevantes = Comunidad.objects.filter(
        tematica__in=temas_comunidades,
        activada=True
    ).distinct()
    comunidades_publicas = comunidades_relevantes.filter(publica=True)
    comunidades_privadas = comunidades_relevantes.filter(publica=False).filter(miembros=request.user)

    comunidades_totales = set(comunidades_publicas) | set(comunidades_privadas)



    # Obtener los perfiles que el usuario sigue
    seguidos = profile.seguidos.all()

    todos_proyectos = Proyecto.objects.filter(
        Q(comunidad__in=comunidades_totales) |
        Q(creador__in=[seguido.usuario for seguido in seguidos])
    ).exclude(creador=user).exclude(tematica__in=no_me_gustan).distinct().order_by('-fecha_creacion')
    # Obtener todas las publicaciones relevantes
    todas_publicaciones = Publicacion.objects.filter(
        Q(comunidad__in=comunidades_totales) |
        Q(autor__in=[seguido.usuario for seguido in seguidos])
    ).exclude(autor=user).exclude(tematica__in=no_me_gustan).distinct().order_by('-fecha_publicacion')

    # Agrupar las publicaciones por tipo
    publicaciones_comunidades = []
    publicaciones_seguidos = []

    proyectos_comunidades = []
    proyectos_seguidos = []

    for pro in todos_proyectos:
        if pro.comunidad in comunidades_totales:
            proyectos_comunidades.append(pro)
        else:
            proyectos_seguidos.append(pro)

    for pub in todas_publicaciones:
        if pub.comunidad in comunidades:
            publicaciones_comunidades.append(pub)
        else:
            publicaciones_seguidos.append(pub)

    proyectos = []
    while proyectos_comunidades or proyectos_seguidos:
        if proyectos_comunidades:
            proyectos.append(proyectos_comunidades.pop(0))
        if proyectos_seguidos:
            proyectos.append(proyectos_seguidos.pop(0))

    # Mezclar las listas manteniendo el orden general
    publicaciones = []
    while publicaciones_comunidades or publicaciones_seguidos:
        if publicaciones_comunidades:
            publicaciones.append(publicaciones_comunidades.pop(0))
        if publicaciones_seguidos:
            publicaciones.append(publicaciones_seguidos.pop(0))

    # Actualizar puntos del usuario


    url = request.path
    is_first_time = is_first_visit(request, url)
    if is_first_time:
        FirstVisit.objects.create(user=request.user, url=url)
    terminos_usuario = TerminosCondicionesUsuario.objects.filter(usuario=request.user).first()
    terminos_aceptados = False
    if terminos_usuario:
        if terminos_usuario.aceptado:
            terminos_aceptados = True

    concursos = False
    if Concurso.objects.all().count() > 0:
        concursos = True

    return render(request, 'inicio.html', {
        'proyectos': proyectos,
        'concurso': contador,
        'is_first_time': is_first_time,
        'terminos': terminos,
        'terminos_aceptados': terminos_aceptados,
        'is_superuser': is_superuser,
        'concursos': concursos,
    })


@login_required
#@permission_required('social.add_comunidad', raise_exception=True)
def crear_comunidad(request):
    if request.method == 'POST':
        form = ComunidadForm(request.POST)
        if form.is_valid():
            comunidad = form.save(commit=False)
            comunidad.administrador = request.user
            comunidad.crowuser = request.user
            comunidad.slug = comunidad.nombre
            comunidad.acepta_donaciones=request.POST.get('acepta_donaciones')
            if request.POST.get('acepta_donaciones')==None:
                comunidad.acepta_donaciones=False
            comunidad.save()
            comunidad.miembros.add(request.user)

            ADMIN_EMAIL = os.environ.get('EMAIL_HOST_USER')
            '''send_mail(
                'Nueva solicitud de cuenta',
                f'El usuario {request.user} ha solicitado una comunidad. Con el nombre de {comunidad.nombre}.',
                ADMIN_EMAIL,
                ['cespedesalejandro247@gmail.com'],
                fail_silently=False,
            )'''
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='crear_comunidad').first()
                update_user_points(request.user.id, accion.id, accion.puntos)
            return redirect('inicio')
    else:
        form = ComunidadForm()
    return render(request, 'crear_comunidad.html', {'form': form})

@login_required
def lista_publicaciones(request,username):
    user = User.objects.get(username=username)
    profile = PerfilUsuario.objects.get(usuario=user)
    publicaciones = Publicacion.objects.filter(autor = user).order_by('-fecha_publicacion')

    return render(request, 'lista_publicaciones.html', {'publicaciones': publicaciones, 'user': user, })

@login_required
def detalle_comunidad(request, slug):


    user = request.user
    profile = PerfilUsuario.objects.get(usuario=user)
    comunidad = get_object_or_404(Comunidad, slug=slug, activada=True)

    revisar_campaigns(comunidad=comunidad)

    desafios = Desafio.objects.filter(comunidad=comunidad)
    campaigns = Campaña.objects.filter(desafio__comunidad=comunidad).order_by('-id')
    es_admin = comunidad.administrador == request.user
    es_crowdsourcer= user.groups.filter(name="Crowdsourcer").exists()
    seguidos = profile.seguidos.all()
    es_miembro = comunidad.es_miembro(user)
    is_superuser= user.is_superuser
    tematicas = ""
    mis_tematicas = comunidad.tematica.all()
    no_me_gustan = [no.id for no in profile.no_me_gusta.all()]
    proyectos = Proyecto.objects.filter(comunidad=comunidad).exclude(tematica__in=no_me_gustan).order_by('-id')

    for tema in mis_tematicas:
        tematicas += f"{tema}, "
    tematicas = tematicas[:-2]+'.'

    print(user.groups.filter(name="Crowdsourcer").exists())
    # Obtener todas las publicaciones relevantes
    publicaciones = Publicacion.objects.filter(
        Q(comunidad=comunidad) |
        Q(autor__in=[seguido.usuario for seguido in seguidos])
    ).exclude(autor=user).exclude(tematica__in=no_me_gustan).distinct().order_by('-fecha_publicacion')
    print(publicaciones)
    filtro = request.GET.get('filtro', 'todas')
    if filtro!=None and filtro != 'todas':
        publicaciones = publicaciones.filter(tematica__nombre=filtro)
    print(filtro)
    print(publicaciones)

    if comunidad.publica:
        campaigns= campaigns.exclude(desafio__tipo_desafio='donacion')

    hay = False
    if campaigns.filter(activa=True).count() > 0:
        hay = True

    return render(request, 'detalle_comunidad.html', {
    'publicaciones': publicaciones,
    'comunidad': comunidad,
    'proyectos': proyectos,
    'desafios': desafios,
    'es_admin': es_admin,
    'es_crowdsourcer': es_crowdsourcer,
    'es_miembro': es_miembro,
    'campaigns': campaigns,
    'is_superuser': is_superuser,
    'tematicas': tematicas,
    'mis_tematicas': mis_tematicas,
    'filtro_actual': filtro,
    'hay': hay,
})

def revisar_campaigns(comunidad):
    campaigns = Campaña.objects.filter(desafio__comunidad=comunidad, desafio__activada=True)
    for campaign in campaigns:
        if campaign.desafio.fecha_fin != None and campaign.desafio.fecha_fin < timezone.now():
            campaign.desafio.activada = False
            campaign.activa = False
            campaign.desafio.save()
            campaign.save()

@login_required
#@permission_required('social.add_proyecto', raise_exception=True)
def crear_proyecto(request,slug):
    comunidad = Comunidad.objects.get(slug=slug)
    tematicas = comunidad.tematica.all()


    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.comunidad=comunidad
            tematica = Tematica.objects.get(nombre=request.POST.get('tematica'))
            proyecto.tematica = tematica
            proyecto.creador = request.user
            proyecto.slug=proyecto.titulo
            proyecto.save()
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='crear_proyecto').first()
                update_user_points(request.user.id, accion.id, accion.puntos)
            return redirect('detalle_proyecto', slug=proyecto.slug)
    else:
        form = ProyectoForm()
    return render(request, 'crear_proyecto.html', {'form': form, 'comunidad': slug, 'tematicas': tematicas,})

@login_required
def detalle_proyecto(request, slug):
    proyecto = get_object_or_404(Proyecto, slug=slug)
    no_me_gusta = False
    yo = False
    if proyecto.creador == request.user:
        yo = True
    if proyecto.tematica in request.user.perfilusuario.no_me_gusta.all():
        no_me_gusta = True

    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto, 'no_me_gusta': no_me_gusta, 'yo':yo})

@login_required
def crear_desafio(request,slug):
    comunidad = Comunidad.objects.get(slug=slug)
    if request.method == 'POST':
        form = DesafioForm(request.POST)
        if form.is_valid():
            desafio = form.save(commit=False)
            desafio.comunidad=comunidad
            desafio.creador = request.user
            desafio.slug= desafio.titulo
            desafio.save()

            campaign = Campaña.objects.create(desafio=desafio)
            campaign.slug=campaign.desafio.titulo
            campaign.save()
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='crear_desafio').first()
                update_user_points(request.user.id, accion.id, accion.puntos)

            return redirect('detalle_campaign', slug=campaign.slug)
        else:
            print("form: ",form)
            print("form.errors: ",form.errors)
    else:
        form = DesafioForm()

    publica = False
    if comunidad.publica:
        publica = True
    acepta_donaciones = False
    if comunidad.acepta_donaciones:
        acepta_donaciones = True

    return render(request, 'crear_desafio.html', {'form': form,'comunidad':slug,'publica':publica,'acepta_donaciones':acepta_donaciones})

@login_required
def detalle_desafio(request, slug):
    desafio = get_object_or_404(Desafio, slug=slug)
    return render(request, 'detalle_desafio.html', {'desafio': desafio})

def puntuar_desafio(request, desafio_id, punto):
    campaign = get_object_or_404(Campaña, id=desafio_id)
    desafio = campaign.desafio

    puntaje_desafio, created = PuntajeDesafio.objects.update_or_create(
            desafio=desafio,
            usuario=request.user,
            defaults={'puntaje': punto}
        )

    # Calcula el promedio de puntajes
    promedio_puntaje = PuntajeDesafio.objects.filter(desafio=desafio).aggregate(Avg('puntaje'))['puntaje__avg'] or 0

    # Actualiza el promedio de puntaje en el modelo Desafio (opcional)
    desafio.save()
    if not request.user.is_superuser:
        accion = Accion.objects.filter(nombre='puntuar desafio').first()
        update_user_points(request.user.id, accion.id, accion.puntos)

    return redirect('detalle_campaign', slug=slug)

def buscar(request):
    q = request.GET.get('q')
    busqueda = q
    if not q:
        q=""
        busqueda="TODO"

    usuarios = User.objects.filter(
        Q(first_name__icontains=q) |
        Q(last_name__icontains=q)
    ).select_related('perfilusuario')
    comunidades = Comunidad.objects.filter( Q(nombre__icontains=q) & Q(activada=True))
    proyectos = Proyecto.objects.filter( Q(titulo__icontains=q))
    desafios = Desafio.objects.filter(Q(titulo__icontains=q))

    return render(request, 'buscar.html', {'busqueda':busqueda, 'usuarios': usuarios, 'comunidades': comunidades, 'proyectos': proyectos, 'desafios': desafios})
@login_required
def chat(request, receptor_id):
    receptor = get_object_or_404(User, id=receptor_id)
    room_name = f'{min(request.user.id, receptor.id)}_{max(request.user.id, receptor.id)}'
    mensajes = MensajeChat.objects.filter(room_name=room_name).order_by('fecha_envio')

    # Marcar mensajes como leídos
    mensajes_no_leidos = mensajes.filter(leido=False).exclude(emisor=request.user)
    for mensaje in mensajes_no_leidos:
        mensaje.marcar_como_leido()

    return render(request, 'chat.html', {
        'receptor': receptor,
        'mensajes': mensajes,
        'room_name': room_name
    })

'''
@login_required
def ranking_usuarios(request):
    top_usuarios = PerfilUsuario.objects.order_by('-puntos')[:10]
    return render(request, 'ranking.html', {'top_usuarios': top_usuarios})

from django.contrib.auth.decorators import login_required
'''

@login_required
def perfil_usuario(request, username):
    if request.method == 'POST':
        perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
        foto_perfil = request.FILES.get('foto_perfil')
        if foto_perfil:
            perfil_usuario.foto_perfil = foto_perfil
            perfil_usuario.save()
            return redirect('perfil_usuario', username=request.user.username)

    usuario = get_object_or_404(User, username=username)
    perfil = PerfilUsuario.objects.get(usuario=usuario)
    proyectos = Proyecto.objects.filter(creador=usuario).order_by('-fecha_creacion')
    clasificacion = get_clasificacion(perfil.puntos)
    sigue_a = perfil.sigue_a(request.user)
    yo= not usuario==request.user
    comunidades=Comunidad.objects.filter(miembros=usuario)
    publicaciones = Publicacion.objects.filter(autor=usuario).order_by('-fecha_publicacion')
    pubcount = publicaciones.count()
    procount = proyectos.count()
    donaciones = DonacionComunidad.objects.filter(donador=request.user).order_by('-fecha_creacion')
    cantidad_donaciones = donaciones.__len__()
    crowuser = False
    if usuario.groups.filter(name='Crowdsourcer').exists():
        crowuser = True

    return render(request, 'perfil_usuario.html', {
        'usuario': usuario,
        'perfil': perfil,
        'proyectos': proyectos,
        'sigue_a': sigue_a,
        'clasificacion': clasificacion,
        'yo':yo,
        'comunidades':comunidades,
        'publicaciones':publicaciones,
        'pubcount': pubcount,
        'procount': procount,
        'donaciones': donaciones,
        'cantidad_donaciones': cantidad_donaciones,
        'crowuser': crowuser,
    })

from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            #login(request, user)
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='registrarse').first()
                update_user_points(user.id, accion.id, accion.puntos)
            return redirect('login')  # Reemplaza 'home' con la URL a donde quieres redirigir después del registro
    else:

        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def crear_publicacion(request, slug):
    comunidad = Comunidad.objects.get(slug=slug)
    tematicas = comunidad.tematica.all()

    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        print(form.is_valid(),form.errors)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.comunidad=comunidad
            publicacion.tematica = Tematica.objects.get(nombre=request.POST.get('tematica'))
            '''# Verificamos si hay al menos una tematica seleccionada
            if not form.cleaned_data['tags']:
                form.add_error('tags', 'Debes seleccionar al menos un Tematica.')
                return render(request, 'crear_publicacion.html', {'form': form})
            '''
            publicacion.save()

            tags = form.cleaned_data.get('tags')
            if tags:
                publicacion.tags.set(tags)

            # Guarda los adjuntos después de guardar la publicación
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='publicar').first()
                update_user_points(request.user.id, accion.id, accion.puntos)
            return redirect('detalle_comunidad', slug=comunidad.slug)
    else:
        form = PublicacionForm()

    return render(request, 'crear_publicacion.html', {'form': form, 'comunidad': slug, 'tematicas': tematicas,})

@login_required
def like_desafio(request, desafio_id):
    desafio = get_object_or_404(Desafio, id=desafio_id)
    campaign = get_object_or_404(Campaña, desafio=desafio_id)

    if request.user in desafio.likes.all():
        print("1")
        desafio.likes.remove(request.user)  # Quitar like si ya existe
    else:
        print("2")
        desafio.likes.add(request.user)  # Agregar like si no existe

    return redirect('detalle_campaign', campaign.slug)

@login_required
def like_comentariod(request, desafio_id,comentario_id):
    desafio = get_object_or_404(Desafio, id=desafio_id)
    campaign = get_object_or_404(Campaña, desafio=desafio_id)
    respuesta = get_object_or_404(Respuesta, id=comentario_id)
    if request.user in respuesta.likes.all():
        print("1")
        respuesta.likes.remove(request.user)  # Quitar like si ya existe
    else:
        print("2")
        respuesta.likes.add(request.user)  # Agregar like si no existe

    return redirect('detalle_campaign', campaign.slug)

def like(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        like, created = Like.objects.get_or_create(
            publicacion=publicacion,
            autor=request.user
        )
        if created:
            publicacion.like
        else:
            publicacion.like
        publicacion.save()
        return JsonResponse({'likes': publicacion.likes})
    return HttpResponse(status=405)

def like_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    if request.method == 'POST':
        like, created = Like_Comentario.objects.get_or_create(
            comentario=comentario,
            autor=request.user
        )
        if created:
            comentario.like
        else:
            comentario.like
        comentario.save()
        return JsonResponse({'likes': comentario.likes})
    return HttpResponse(status=405)


@login_required
def crear_comentario(request, pk):
    publicacion = Publicacion.objects.get(pk=pk)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.autor = request.user
            comentario.save()
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='comentar').first()
                update_user_points(request.user.id, accion.id, accion.puntos)

            return redirect('detalle_comunidad', publicacion.comunidad.slug)
    else:
        form = ComentarioForm()
    return render(request, 'crear_comentario.html', {'form': form, 'publicacion': publicacion})

@login_required
def crear_comentario_pub(request, pk):
    publicacion = Publicacion.objects.get(pk=pk)
    if request.method == 'POST':
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.publicacion = publicacion
            comentario.autor = request.user
            comentario.save()
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='comentar').first()
                update_user_points(request.user.id, accion.id, accion.puntos)

            return redirect('lista_publicaciones', publicacion.autor.username)
    else:
        form = ComentarioForm()
    return render(request, 'crear_comentario.html', {'form': form, 'publicacion': publicacion})

@login_required
def crear_comentario_pro(request, pk):
    proyecto = Proyecto.objects.get(pk=pk)
    if request.method == 'POST':
        form = ComentarioProyectoForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.proyecto = proyecto
            comentario.autor = request.user
            comentario.save()
            if not request.user.is_superuser:
                accion = Accion.objects.filter(nombre='comentar proyecto').first()
                update_user_points(request.user.id, accion.id, accion.puntos)
            return render(request, 'detalle_proyecto.html', {'proyecto': proyecto})
    else:
        form = ComentarioProyectoForm()
    return render(request, 'crear_comentario.html', {'form': form, 'proyecto': proyecto})

@login_required
def mostrar_publicaciones(request):
    publicaciones = obtener_publicaciones_no_vistas(request)
    for publicacion in publicaciones:
        registrar_publicacion_vista_script(request, publicacion.id)
    return render(request, 'base.html', {'publicaciones': publicaciones})

@login_required
def registrar_publicacion_vista(request, publicacion_id):
    publicacion = Publicacion.objects.get(id=publicacion_id)
    usuario = request.user
    PublicacionVista.objects.create(publicacion=publicacion, usuario=usuario)
    return HttpResponse('Publicación vista registrada')

@login_required
def obtener_publicaciones_no_vistas(request):
    usuario = request.user
    publicaciones_vistas = PublicacionVista.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    tags = request.GET.getlist('tags')
    if tags:
        publicaciones = Publicacion.objects.filter(tags__name__in=tags).exclude(id__in=publicaciones_vistas)
    else:
        publicaciones = Publicacion.objects.exclude(id__in=publicaciones_vistas)
    return render(request, 'publicaciones.html', {'publicaciones': publicaciones})

@login_required
def registrar_publicacion_vista_script(request, publicacion_id):
    registrar_publicacion_vista(request, publicacion_id)
    return HttpResponse('Publicación vista registrada')

from django.http import HttpResponse
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatWS    (AsyncWebsocketConsumer):
    async def connect(self):
        print("Ruta utilizada:", self.scope['path'])
        # Obtener el receptor_id del URL
        self.receptor_id = self.scope['url_route']['kwargs']['receptor_id']
        self.emisor_id = self.scope['user'].id
        print("Receptor ID:", self.receptor_id)
        print("Emisor ID:", self.emisor_id)

        # Crear un grupo de chat para el emisor y el receptor
        self.group_name = f"chat_{self.emisor_id}-{self.receptor_id}"
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        # Enviar un mensaje de bienvenida al emisor
        await self.send(text_data="¡Bienvenido al chat!")

    async def disconnect(self, close_code):
        # Eliminar el grupo de chat cuando el emisor se desconecta
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Obtener el mensaje del emisor
        mensaje = text_data

        # Crear un objeto Mensaje en la base de datos
        mensaje_obj = MensajeChat.objects.create(
            emisor=self.scope['user'],
            receptor_id=self.receptor_id,
            contenido=mensaje
        )

        # Enviar el mensaje al receptor
        await self.channel_layer.group_send(
            self.group_name,
            {
                "type": "chat_message",
                "mensaje": mensaje_obj.contenido
            }
        )

    async def chat_message(self, event):
        # Enviar el mensaje al emisor
        await self.send(text_data=event["mensaje"])

def aceptar_terminos_registro(request):
    terminos = TerminosCondiciones.objects.all().first()
    return render(request, 'aceptar_terminos_registro.html', {'terminos': terminos})

def aceptar_terminos(request):
    terminos = TerminosCondiciones.objects.all().first()
    terminos_usuario = TerminosCondicionesUsuario.objects.filter(usuario=request.user).first()
    terminos_aceptados = False
    if terminos_usuario:
        if terminos_usuario.aceptado:
            terminos_aceptados = True


    if request.method == 'POST':
        usuario = request.user
        aceptado_en = timezone.now()
        if not terminos_aceptados:
            if not terminos_usuario == None:
                terminos_usuario.aceptado_en = timezone.now()
                terminos_usuario.save()
            else:
                TerminosCondicionesUsuario.objects.create(
                    usuario=usuario,
                    terminos=terminos,
                    aceptado_en=aceptado_en
                )
        else:
            if not terminos_usuario == None:
                terminos_usuario.aceptado_en = timezone.now()
                terminos_usuario.save()

        return redirect('inicio')

    return render(request, 'aceptar_terminos.html', {'terminos': terminos, 'terminos_aceptados': terminos_aceptados, 'terminos_usuario': terminos_usuario})

@login_required
def buscar_usuarios(request):
    usuarios = User.objects.all()
    sigue_a = {}
    for usuario in usuarios:
        sigue_a[usuario] = request.user.perfilusuario.sigue_a(usuario)
    return render(request, 'buscar_usuarios.html', {'usuarios': usuarios, 'sigue_a': sigue_a})


def seguir_usuario(request, slug):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    usuario = PerfilUsuario.objects.get(slug=slug)
    perfil_usuario.seguir_usuario(usuario.usuario)
    accion = Accion.objects.filter(nombre='seguir').first()
    if not request.user.is_superuser:
        update_user_points(request.user.id, accion.id, accion.puntos)
    return redirect('perfil_usuario', username=usuario.usuario.username)


def dejar_de_seguir_usuario(request, pk):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    usuario = PerfilUsuario.objects.get(id=pk).usuario
    perfil_usuario.dejar_de_seguir_usuario(usuario)
    accion = Accion.objects.filter(nombre='seguir').first()
    if not request.user.is_superuser:
        update_user_points(request.user.id, accion.id, -(accion.puntos))
    return redirect('perfil_usuario', username=usuario.username)


'''@login_required
def lista_publicaciones(request):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    seguidos = perfil_usuario.seguidos.all()
    publicaciones = Publicacion.objects.filter(autor__in=[seguido.usuario for seguido in seguidos])
    publicaciones_propias = Publicacion.objects.filter(autor=request.user)
    publicaciones = publicaciones | publicaciones_propias
    if not publicaciones.exists():
        publicaciones = None
    return render(request, 'lista_publicaciones.html', {'publicaciones': publicaciones})
'''


def action_view(request, action_id):
    accion = Accion.objects.get(id=action_id)
    if request.user.is_authenticated:
        update_user_points(request.user.id, action_id, accion.puntos)
    return render(request, 'accion.html', {'accion': accion})

def user_profile_view(request, user_id):
    user = User.objects.get(id=user_id)
    profile, _ = PerfilUsuario.objects.get_or_create(user=user)
    return render(request, 'profile.html', {'user': user, 'profile': profile})


@login_required
def crear_concurso(request):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        fecha_inicio = request.POST['fecha_inicio']
        fecha_fin = request.POST['fecha_fin']

        premio_id = request.POST['premio']
        premio = Premio.objects.get(id=premio_id)
        documento = request.FILES.get('documento')

        Concurso.objects.create(
            documento=documento,
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            premio=premio
        )
        return redirect('listar_concursos')

    premios = Premio.objects.all()
    return render(request, 'crear_concurso.html', {'premios': premios})

@login_required
def listar_concursos(request):
    concursos = Concurso.objects.all().order_by('-fecha_fin')
    return render(request, 'listar_concursos.html', {'concursos': concursos})


def concurso_resultados(request):
    concurso_actual = Concurso.objects.latest('fecha_fin')
    premio = concurso_actual.premio
    # Ordenar por ranking y tomar el primero
    ganador = PerfilUsuario.objects.order_by('-puntos').first()
    superuser = ganador
    flag = False
    if ganador.usuario.is_superuser:
        superuser = ganador
        flag = True
        ganador = PerfilUsuario.objects.filter(not self == superuser).order_by('-puntos').first()
    usuario= User.objects.get(id=ganador.usuario.id)
    if flag:
        top_usuarios = PerfilUsuario.objects.filter(not self == superuser).order_by('-puntos')[:10]
    else:
        top_usuarios = PerfilUsuario.objects.order_by('-puntos')[:10]
    return render(request, 'concurso_resultados.html', {
        'concurso': concurso_actual,
        'ganador': ganador,
        'usuario':usuario,
        'top_usuarios':top_usuarios,
        'premio': premio
    })


def lista_comunidades(request):
    comunidades_activas = Comunidad.objects.filter(activada=True)
    return render(request, 'lista_comunidades.html', {'comunidades': comunidades_activas})




@login_required
def detalle_campaign(request, slug):
    campaign = get_object_or_404(Campaña, slug=slug)
    desafio=campaign.desafio
    like_count = desafio.likes.count()

    like_campaign= False
    like_respuestas= []

    for comentario in campaign.respuestas.all():
        if request.user in comentario.likes.all():
            like_respuestas.append(comentario)

    if request.user in desafio.likes.all():
        like_campaign=True

    lleno = False
    if (int(desafio.cantidad_donada)==int(desafio.objetivo_monto)):
        lleno=True

    tipo = False
    if campaign.tipo=="donacion":
        tipo=True
    if request.method == 'POST' and campaign.activa:
        respuesta_form = RespuestaForm(request.POST)
        if respuesta_form.is_valid():
            respuesta = respuesta_form.save(commit=False)
            respuesta.autor = request.user
            respuesta.campaign = campaign
            respuesta.save()
            if not request.user.is_superuser:
                accion: Accion | None= Accion.objects.filter(nombre='responder_campaign').first()
                update_user_points(request.user.id, accion.id, accion.puntos)

            return redirect('detalle_campaign', slug=campaign.slug)
    else:
        respuesta_form = RespuestaForm()

    puntuaciones = Accion.objects.filter(nombre__startswith='puntos')

    return render(request, 'detalle_campaign.html', {
        'campaign': campaign,
        'respuesta_form': respuesta_form,
        'puntuaciones': puntuaciones,
        'is_creador': request.user == campaign.desafio.creador,
        'campaign_activa': campaign.activa,
        'tipo':tipo,
        'total_likes':like_count,
        'like_campaign':like_campaign,
        'like_respuestas':like_respuestas,
        'lleno':lleno,
    })

@login_required
def lista_campaigns(request, slug):
    campaigns = Campaña.objects.filter(desafio__comunidad__slug=slug).order_by('-id')
    comunidad= Comunidad.objects.filter(slug=slug).first()
    filtro = request.GET.get('filtro', 'todas')
    if filtro == 'activas':
        campaigns = campaigns.filter(activa=True)
    elif filtro == 'no_activas':
        campaigns = campaigns.filter(activa=False)

    if comunidad != None and comunidad.publica:
        campaigns = campaigns.exclude(desafio__tipo_desafio='donacion')

    return render(request, 'lista_campaigns.html', {
        'comunidad': comunidad,
        'campaigns': campaigns,
        'filtro_actual': filtro
    })

@login_required
def lista_proyectos(request, slug):
    comunidad= Comunidad.objects.filter(slug=slug).first()
    user = request.user
    profile = PerfilUsuario.objects.get(usuario=user)
    no_me_gustan = [no.id for no in profile.no_me_gusta.all()]
    proyectos = Proyecto.objects.filter(comunidad=comunidad).exclude(tematica__in=no_me_gustan).order_by('-id')

    return render(request, 'lista_proyectos.html', {
        'comunidad': comunidad,
        'proyectos': proyectos,
    })

@login_required
def lista_miembros(request, slug):
    comunidad= Comunidad.objects.filter(slug=slug).first()

    return render(request, 'lista_miembros.html', {
        'comunidad': comunidad,
    })

@login_required
def puntuar_respuesta(request, pk, estrellas):
    respuesta = get_object_or_404(Respuesta, pk=pk)
    if request.method == 'POST' and request.user == respuesta.campaign.desafio.creador:
        respuesta.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def guardar_donacion(request,slug):
    desafio= Desafio.objects.get(slug=slug)
    campaig= Campaña.objects.get(desafio=desafio)
    min= int(desafio.min_monto)
    max = int(desafio.max_monto)
    antes = desafio.cantidad_donada
    maximo= int(desafio.objetivo_monto-antes)
    if request.method == 'POST':
        identificador_transferencia = request.POST['identificador_transferencia']
        cantidad = request.POST['cantidad']
        # Aquí deberías validar los datos antes de guardarlos
        # Por ejemplo:

        desafio.cantidad_donada+=Decimal(cantidad)

        if (float(cantidad)<desafio.min_monto or float(cantidad)>desafio.max_monto or desafio.cantidad_donada>desafio.objetivo_monto):
            if (desafio.cantidad_donada>desafio.objetivo_monto):

                return render(request, 'crear_donacion.html', {'error': 'Por favor, el monto debe ser entre {desafio.min_monto} y {maximo}',
                                                                'slug':campaig.slug})
            return render(request, 'crear_donacion.html', {'error': 'Por favor, el monto debe ser entre {desafio.min_monto} y {desafio.max_monto}',
                                                            'slug':campaig.slug})
        desafio.save()
        # Guardar la donación en la base de datos
        DonacionComunidad.objects.create(
            donador=request.user,
            campaign=desafio,
            identificador_transferencia=identificador_transferencia,
            cantidad=cantidad,
        )
        if not request.user.is_superuser:
            accion = Accion.objects.filter(nombre='donar').first()
            update_user_points(request.user.id, accion.id, accion.puntos)
        # Si todo salió bien, redirige al usuario a la lista de donaciones
        return redirect('detalle_campaign', slug=campaig.slug)
    campaign = desafio.campaign
    qr = Cuenta.objects.first()
    # Si es una solicitud GET, muestra el formulario vacío con los datos del usuario prellenados
    form = DonacionComunidadForm(initial={
        'identificador_transferencia': '',
        'cantidad': ''
    })

    return render(request, 'crear_donacion.html', {
        'form': form,
        'qr':qr,
        'campaign': campaign,
        'min':min,
        'max':max,
        'slug': campaign.slug,
        'maximo':maximo,
        })


@login_required
def chat_comunidad(request, slug):
    comunidad = get_object_or_404(Comunidad, slug=slug)
    if request.user not in comunidad.miembros.all():
        return HttpResponseForbidden("No eres miembro de esta comunidad.")

    mensajes = MensajeChatComunidad.objects.filter(comunidad=comunidad).order_by('fecha_envio')

    # Marcar mensajes como leídos
    for mensaje in mensajes:
        if request.user not in mensaje.leido_por.all():
            mensaje.marcar_como_leido(request.user)

    return render(request, 'chat_comunidad.html', {
        'comunidad': comunidad,
        'mensajes': mensajes,
    })


@login_required
def editar_perfil(request):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    user = request.user
    if request.method == 'POST':
        if request.POST.get('foto_perfil') == "" or request.POST.get('foto_perfil') is None:
            request.POST._mutable = perfil_usuario.foto_perfil.url
        perfil_form = EditUserProfilePersonalForm(request.POST, request.FILES, instance=perfil_usuario)
        user_form = EditUserForm(request.POST, instance=user)

        if perfil_form.is_valid() and user_form.is_valid():
            perfil_form.save()
            user_form.save()
            return redirect('perfil_usuario', request.user.username)
    else:
        perfil_form = EditUserProfilePersonalForm(instance=perfil_usuario)
        user_form = EditUserForm(instance=user)

    return render(request, 'editar_perfil.html', {
        'form_perfil': perfil_form,
        'form_usuario': user_form,
        'user': user,
    })

@login_required
def editar_proyecto(request, slug):
    proyecto = get_object_or_404(Proyecto, slug=slug)
    form = ProyectoForm(instance=proyecto)
    if request.method == 'POST':
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
        if form.is_valid():
            form.save()
            return redirect('detalle_proyecto', slug=proyecto.slug)
    return render(request, 'editar_proyecto.html', {'form': form, 'proyecto': proyecto})

@login_required
def eliminar_proyecto(request, slug):
    proyecto = get_object_or_404(Proyecto, slug=slug)
    proyecto.delete()
    return redirect('detalle_comunidad', slug=proyecto.comunidad.slug)

@login_required
def unirse_comunidad(request, slug):
    comunidad = Comunidad.objects.get(slug=slug)
    if comunidad.publica:
        comunidad.miembros.add(request.user)
        print(f"El usuario {request.user.username} se unió a la comunidad {comunidad.nombre}")
        return redirect('detalle_comunidad', slug=slug)
    else:
        return redirect('detalle_comunidad', slug=slug)

@login_required
def salir_comunidad(request, slug):
    comunidad = Comunidad.objects.get(slug=slug)
    comunidad.miembros.remove(request.user)
    print("salio")
    return redirect('detalle_comunidad', slug=slug)

@login_required
def solicitar_membresia(request, slug):
    comunidad = get_object_or_404(Comunidad, slug=slug)
    solicitud_pendiente = SolicitudMembresia.objects.filter(comunidad=comunidad, usuario=request.user).first()
    creada = False
    if solicitud_pendiente:
        creada = True

    if request.method == 'POST':
        # Verificar que la comunidad es privada
        if comunidad.publica:
            return redirect('detalle_comunidad', slug=slug)

        # Crear la solicitud de membresía
        solicitud, created = SolicitudMembresia.objects.get_or_create(comunidad=comunidad, usuario=request.user)
        solicitud.save()
        if created:
            # Notificar que la solicitud fue enviada
            return redirect('detalle_comunidad', slug)
        else:
            # Si ya existe una solicitud pendiente
            creada = True

    return render(request, 'solicitud_membresia.html', {'comunidad': comunidad , 'creada': creada})


def solicitar_crowuser(request):
    if request.method == 'POST':
        form = SolicitudCrowuserForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()

            ADMIN_EMAIL = os.environ.get('EMAIL_HOST_USER')
            '''send_mail(
                'Nueva solicitud de cuenta',
                f'El usuario {request.user} ha solicitado una comunidad. Con el nombre de {comunidad.nombre}.',
                ADMIN_EMAIL,
                ['cespedesalejandro247@gmail.com'],
                fail_silently=False,
            )'''

            return redirect('inicio')
    else:
        form = SolicitudCrowuserForm()
    return render(request, 'solicitud_crowuser.html', {'form': form})




@login_required()
def ranking_usuarios(request):
    ranking = []
    form = RangoFechaForm(request.POST or None)
    concursos = False
    if Concurso.objects.all().count() > 0:
        concursos = True

    # Definir un rango de fechas predeterminado si no se proporciona
    if request.method == 'POST' and form.is_valid():
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
    else:
        # Establecer un rango de fechas predeterminado (por ejemplo, los últimos 30 días)
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=60)

    # Obtener el ranking de usuarios en base al rango de fechas
    ranking = (
        AccionUsuario.objects.filter(
            timestamp__range=(fecha_inicio, fecha_fin),
            user__is_superuser=False,
            user__id__in=(
        User.objects.exclude(groups__name='Administrador de Comunidad').values_list('id', flat=True)
    ))
        .values('user__username')
        .annotate(total_puntos=Sum('puntos'))
        .order_by('-total_puntos')
    )[:10]
    print(ranking)
    return render(request, 'ranking.html', {'ranking': ranking, 'form': form, 'concursos': concursos})

@login_required()
def ver_donaciones(request):
    donaciones = DonacionComunidad.objects.filter(donador=request.user).order_by('-fecha_creacion')

    return render(request, 'donaciones.html', {'donaciones':donaciones,})

@login_required()
def no_me_gusta(request,tematica):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    perfil_usuario.no_gusta(tematica)
    previous_url = request.META.get('HTTP_REFERER', '/')
    return redirect(previous_url)
