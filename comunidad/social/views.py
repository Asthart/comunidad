# views.py

from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Comunidad, Proyecto, Desafio, PerfilUsuario, MensajeChat, ActividadUsuario,Publicacion, PublicacionVista,Tag, TerminosCondiciones
from .forms import ComunidadForm, ProyectoForm, DesafioForm, PublicacionForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.utils import timezone

@login_required
def inicio(request):
    comunidades = Comunidad.objects.filter(miembros=request.user,activada=True)
    proyectos = Proyecto.objects.filter(comunidad__in=comunidades)
    desafios = Desafio.objects.filter(comunidad__in=comunidades)
    return render(request, 'inicio.html', {
        'comunidades': comunidades,
        'proyectos': proyectos,
        'desafios': desafios,
    })

@login_required
#@permission_required('social.add_comunidad', raise_exception=True)
def crear_comunidad(request):
    if request.method == 'POST':
        form = ComunidadForm(request.POST)
        if form.is_valid():
            comunidad = form.save(commit=False)
            comunidad.administrador = request.user
            comunidad.save()
            comunidad.miembros.add(request.user)
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_comunidad',
                puntos_ganados=50
            )
            send_mail(
                'Nueva solicitud de cuenta',
                f'El usuario {request.user} ha solicitado una comunidad. Con el nombre de {comunidad.nombre}.',
                'cespedesalejandro247@gmail.com',
                ['cespedesalejandro247@gmail.com'],
                fail_silently=False,
            )
            return redirect('inicio')
    else:
        form = ComunidadForm()
    return render(request, 'crear_comunidad.html', {'form': form})



''''@login_required
def solicitar_cuenta(request):
    if request.method == 'POST':
        form = SolicitudCuentaForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.usuario = request.user
            solicitud.save()
            # Enviar correo al administrador
            send_mail(
                'Nueva solicitud de cuenta',
                f'El usuario {solicitud.nombre} ha solicitado una comunidad.',
                'cespedesalejandro247@gmail.com',
                ['cespedesalejandro247@gmail.com'],
                fail_silently=False,
            )
            return redirect('solicitud_enviada')
    else:
        form = SolicitudCuentaForm()
    return render(request, 'comunidad/solicitar_cuenta.html', {'form': form})
'''



@login_required
def detalle_comunidad(request, pk):
    comunidad = get_object_or_404(Comunidad, pk=pk, activada=True)
    proyectos = Proyecto.objects.filter(comunidad=comunidad)
    desafios = Desafio.objects.filter(comunidad=comunidad)
    es_admin = comunidad.administrador == request.user
    return render(request, 'detalle_comunidad.html', {
    'comunidad': comunidad,
    'proyectos': proyectos,
    'desafios': desafios,
    'es_admin': es_admin,

})

@login_required
#@permission_required('social.add_proyecto', raise_exception=True)
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_proyecto',
                puntos_ganados=30
            )
            return redirect('detalle_proyecto', pk=proyecto.pk)
    else:
        form = ProyectoForm()
    return render(request, 'crear_proyecto.html', {'form': form})

@login_required
def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto})

@login_required
#@permission_required('social.add_desafio', raise_exception=True)
def crear_desafio(request):
    if request.method == 'POST':
        form = DesafioForm(request.POST)
        if form.is_valid():
            desafio = form.save(commit=False)
            desafio.creador = request.user
            desafio.save()
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_desafio',
                puntos_ganados=40
            )
            return redirect('detalle_desafio', pk=desafio.pk)
    else:
        form = DesafioForm()
    return render(request, 'crear_desafio.html', {'form': form})

@login_required
def detalle_desafio(request, pk):
    desafio = get_object_or_404(Desafio, pk=pk)
    return render(request, 'detalle_desafio.html', {'desafio': desafio})

@login_required
def buscar(request):
    query = request.GET.get('q')
    proyectos = Proyecto.objects.filter(titulo__icontains=query)
    usuarios = User.objects.filter(username__icontains=query)
    comunidades = Comunidad.objects.filter(nombre__icontains=query)
    return render(request, 'resultados_busqueda.html', {
        'proyectos': proyectos,
        'usuarios': usuarios,
        'comunidades': comunidades
    })

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

@login_required
def ranking_usuarios(request):
    top_usuarios = PerfilUsuario.objects.order_by('-puntos')[:10]
    return render(request, 'ranking.html', {'top_usuarios': top_usuarios})

@login_required
def perfil_usuario(request, username):
    usuario = get_object_or_404(User, username=username)
    perfil = PerfilUsuario.objects.get(usuario=usuario)
    proyectos = Proyecto.objects.filter(creador=usuario)
    actividades = ActividadUsuario.objects.filter(usuario=usuario).order_by('-fecha_hora')[:10]
    return render(request, 'perfil_usuario.html', {
        'usuario': usuario,
        'perfil': perfil,
        'proyectos': proyectos,
        'actividades': actividades
    })
    
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            if request.POST.get('aceptado_terminos') == 'on':
                user = form.save()
                login(request, user)
                return redirect('inicio')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            publicacion.save()
            return redirect('inicio')
    else:
        form = PublicacionForm()
    return render(request, 'crear_publicacion.html', {'form': form})

def mostrar_publicaciones(request):
    publicaciones = obtener_publicaciones_no_vistas(request)
    for publicacion in publicaciones:
        registrar_publicacion_vista_script(request, publicacion.id)
    return render(request, 'base.html', {'publicaciones': publicaciones})

def registrar_publicacion_vista(request, publicacion_id):
    publicacion = Publicacion.objects.get(id=publicacion_id)
    usuario = request.user
    PublicacionVista.objects.create(publicacion=publicacion, usuario=usuario)
    return HttpResponse('Publicación vista registrada')

def obtener_publicaciones_no_vistas(request):
    usuario = request.user
    publicaciones_vistas = PublicacionVista.objects.filter(usuario=usuario).values_list('publicacion_id', flat=True)
    tags = request.GET.getlist('tags')
    if tags:
        publicaciones = Publicacion.objects.filter(tags__name__in=tags).exclude(id__in=publicaciones_vistas)
    else:
        publicaciones = Publicacion.objects.exclude(id__in=publicaciones_vistas)
    return render(request, 'publicaciones.html', {'publicaciones': publicaciones})

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
        

def aceptar_terminos(request):
    terminos = TerminosCondiciones.objects.get(id=1)
    return render(request, 'aceptar_terminos.html', {'terminos': terminos})