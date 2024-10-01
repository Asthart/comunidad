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
from .models import *
from .forms import *
from .utils import update_user_points,get_clasificacion
from django.core.mail import send_mail
from django.views.generic import ListView
'''
@login_required
def inicio(request):
    comunidades = Comunidad.objects.filter(miembros=request.user,activada=True)
    proyectos = Proyecto.objects.filter(comunidad__in=comunidades)
    desafios = Desafio.objects.filter(comunidad__in=comunidades)
    
    accion = Action.objects.filter(name='inicio').first()
    update_user_points(request.user.id, accion.id, accion.points)
    
    return render(request, 'inicio.html', {
        'comunidades': comunidades,
        'proyectos': proyectos,
        'desafios': desafios,
    })
'''
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Comunidad, PerfilUsuario, Publicacion

@login_required
def inicio(request):
    
    ''' 
    sessionid = request.COOKIES.get('sessionid')

    if sessionid:
        # Lógica para validar el sessionid con la aplicación externa
        user = validate_session_with_external_app(sessionid)
        if user:
            # Iniciar sesión en tu aplicación
            login(request, user)
            return redirect('home')  # Redirigir a la página de inicio

    return redirect('login')  
    '''
    
    
    user = request.user
    profile = PerfilUsuario.objects.get(usuario=user)
    contador = Concurso.ultimo_concurso()
    
    # Obtener las comunidades del usuario
    comunidades = Comunidad.objects.filter(miembros=user, activada=True)
    
    # Obtener los perfiles que el usuario sigue
    seguidos = profile.seguidos.all()
    
    # Obtener todas las publicaciones relevantes
    todas_publicaciones = Publicacion.objects.filter(
        Q(comunidad__in=comunidades) | 
        Q(autor__in=[seguido.usuario for seguido in seguidos])
    ).exclude(autor=user).distinct().order_by('-fecha_publicacion')
    
    # Agrupar las publicaciones por tipo
    publicaciones_comunidades = []
    publicaciones_seguidos = []
    
    for pub in todas_publicaciones:
        if pub.comunidad in comunidades:
            publicaciones_comunidades.append(pub)
        else:
            publicaciones_seguidos.append(pub)
    
    # Mezclar las listas manteniendo el orden general
    publicaciones = []
    while publicaciones_comunidades or publicaciones_seguidos:
        if publicaciones_comunidades:
            publicaciones.append(publicaciones_comunidades.pop(0))
        if publicaciones_seguidos:
            publicaciones.append(publicaciones_seguidos.pop(0))
    
    # Actualizar puntos del usuario
    accion = Action.objects.filter(name='inicio').first()
    update_user_points(user.id, accion.id, accion.points)
    
    return render(request, 'inicio.html', {
        'publicaciones': publicaciones,
        'concurso': contador,
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
            ADMIN_EMAIL = os.environ.get('EMAIL_HOST_USER')
            send_mail(
                'Nueva solicitud de cuenta',
                f'El usuario {request.user} ha solicitado una comunidad. Con el nombre de {comunidad.nombre}.',
                ADMIN_EMAIL,
                ['cespedesalejandro247@gmail.com'],
                fail_silently=False,
            )
            accion = Action.objects.filter(name='crear_comunidad').first()
            update_user_points(request.user.id, accion.id, accion.points)
            return redirect('inicio')
    else:
        form = ComunidadForm()
    return render(request, 'crear_comunidad.html', {'form': form})


@login_required
def detalle_comunidad(request, pk):
    user = request.user
    profile = PerfilUsuario.objects.get(usuario=user)
    comunidad = get_object_or_404(Comunidad, pk=pk, activada=True)
    proyectos = Proyecto.objects.filter(comunidad=comunidad)
    desafios = Desafio.objects.filter(comunidad=comunidad)  
    es_admin = comunidad.administrador == request.user
    seguidos = profile.seguidos.all()
    es_miembro = comunidad.es_miembro(user)
    
    # Obtener todas las publicaciones relevantes
    publicaciones = Publicacion.objects.filter(
        Q(comunidad=comunidad) | 
        Q(autor__in=[seguido.usuario for seguido in seguidos])
    ).exclude(autor=user).distinct().order_by('-fecha_publicacion')
    
    
    return render(request, 'detalle_comunidad.html', {
    'publicaciones': publicaciones,
    'comunidad': comunidad,
    'proyectos': proyectos,
    'desafios': desafios,
    'es_admin': es_admin,
    'es_miembro': es_miembro,
})

@login_required
#@permission_required('social.add_proyecto', raise_exception=True)
def crear_proyecto(request,pk):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        if form.is_valid():
            proyecto = form.save(commit=False)
            comunidad = Comunidad.objects.get(id=pk)
            proyecto.comunidad=comunidad
            
            proyecto.creador = request.user
            proyecto.save()
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_proyecto',
                puntos_ganados=30
            )
            accion = Action.objects.filter(name='crear_proyecto').first()
            update_user_points(request.user.id, accion.id, accion.points)
            return redirect('detalle_proyecto', pk=proyecto.pk)
    else:
        form = ProyectoForm()
    return render(request, 'crear_proyecto.html', {'form': form})

@login_required
def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto})

@login_required
def crear_desafio(request,pk):
    if request.method == 'POST':
        form = DesafioForm(request.POST)
        if form.is_valid():
            desafio = form.save(commit=False)
            comunidad = Comunidad.objects.get(id=pk)
            desafio.comunidad=comunidad
            desafio.creador = request.user
            desafio.save()
            
            campaign = Campaign.objects.create(desafio=desafio)
            
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_desafio',
                puntos_ganados=40
            )
            accion = Action.objects.filter(name='crear_desafio').first()
            update_user_points(request.user.id, accion.id, accion.points)
            
            return redirect('detalle_campaign', pk=campaign.pk)
    else:
        form = DesafioForm()
    
    return render(request, 'crear_desafio.html', {'form': form})

@login_required
def detalle_desafio(request, pk):
    desafio = get_object_or_404(Desafio, pk=pk)
    return render(request, 'detalle_desafio.html', {'desafio': desafio})

def puntuar_desafio(request, desafio_id, punto):
    campaign = get_object_or_404(Campaign, id=desafio_id)
    desafio = campaign.desafio
    
    puntaje_desafio, created = PuntajeDesafio.objects.update_or_create(
            desafio=desafio,
            usuario=request.user,
            defaults={'puntaje': punto}
        )
    
    # Calcula el promedio de puntajes
    promedio_puntaje = PuntajeDesafio.objects.filter(desafio=desafio).aggregate(Avg('puntaje'))['puntaje__avg'] or 0
    
    # Actualiza el promedio de puntaje en el modelo Desafio (opcional)
    desafio.puntaje = promedio_puntaje
    desafio.save()
    
    return redirect('detalle_campaign', pk=desafio_id)

def buscar(request):
    q = request.GET.get('q')
    if q:
        usuarios = User.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q)
        ).select_related('perfilusuario')
        comunidades = Comunidad.objects.filter( Q(nombre__icontains=q))
        proyectos = Proyecto.objects.filter( Q(titulo__icontains=q))
        desafios = Desafio.objects.filter(Q(titulo__icontains=q))
        return render(request, 'buscar.html', {'usuarios': usuarios, 'comunidades': comunidades, 'proyectos': proyectos, 'desafios': desafios})
    else:
        return redirect('inicio')
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

from django.contrib.auth.decorators import login_required

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
    proyectos = Proyecto.objects.filter(creador=usuario)
    clasificacion = get_clasificacion(perfil.puntos)
    actividades = ActividadUsuario.objects.filter(usuario=usuario).order_by('-fecha_hora')[:10]
    sigue_a = perfil.sigue_a(request.user)
    yo= not usuario==request.user
    return render(request, 'perfil_usuario.html', {
        'usuario': usuario,
        'perfil': perfil,
        'proyectos': proyectos,
        'actividades': actividades,
        'sigue_a': sigue_a,
        'clasificacion': clasificacion,
        'yo':yo,
    })
    
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            accion = Action.objects.filter(name='registrarse').first()
            update_user_points(request.user.id, accion.id, accion.points)
            return redirect('inicio')  # Reemplaza 'home' con la URL a donde quieres redirigir después del registro
    else:
        form = CustomUserCreationForm()

    return render(request, 'register.html', {'form': form})

@login_required
def crear_publicacion(request):
    if request.method == 'POST':
        form = PublicacionForm(request.POST, request.FILES)
        if form.is_valid():
            publicacion = form.save(commit=False)
            publicacion.autor = request.user
            
            # Verificamos si hay al menos un tag seleccionado
            if not form.cleaned_data['tags']:
                form.add_error('tags', 'Debes seleccionar al menos un tag.')
                return render(request, 'crear_publicacion.html', {'form': form})
            
            publicacion.save()
            
            tags = form.cleaned_data.get('tags')
            if tags:
                publicacion.tags.set(tags)
                
            # Guarda los adjuntos después de guardar la publicación
            accion = Action.objects.filter(name='publicar').first()
            update_user_points(request.user.id, accion.id, accion.points)
            return redirect('inicio')
    else:
        form = PublicacionForm()
    
    return render(request, 'crear_publicacion.html', {'form': form})

@login_required
def dar_like(request, pk):
    publicacion = Publicacion.objects.get(pk=pk)
    like, created = Like.objects.get_or_create(publicacion=publicacion, autor=request.user)
    if not created:
        like.delete()
    return redirect('inicio')

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
            return redirect('inicio')
    else:
        form = ComentarioForm()
    return render(request, 'crear_comentario.html', {'form': form, 'publicacion': publicacion})

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
        

def aceptar_terminos(request):
    terminos = TerminosCondiciones.objects.get(id=1)
    return render(request, 'aceptar_terminos.html', {'terminos': terminos})

@login_required
def buscar_usuarios(request):
    usuarios = User.objects.all()
    sigue_a = {}
    for usuario in usuarios:
        sigue_a[usuario] = request.user.perfilusuario.sigue_a(usuario)
    return render(request, 'buscar_usuarios.html', {'usuarios': usuarios, 'sigue_a': sigue_a})

@login_required
def seguir_usuario(request, pk):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    usuario = PerfilUsuario.objects.get(id=pk).usuario
    perfil_usuario.seguir_usuario(usuario)
    accion = Action.objects.filter(name='seguir').first()
    update_user_points(request.user.id, accion.id, accion.points)
    return redirect('perfil_usuario', username=usuario.username)

@login_required
def dejar_de_seguir_usuario(request, pk):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    usuario = PerfilUsuario.objects.get(id=pk).usuario
    perfil_usuario.dejar_de_seguir_usuario(usuario)
    return redirect('perfil_usuario', username=usuario.username)

@login_required
def lista_publicaciones(request):
    perfil_usuario = PerfilUsuario.objects.get(usuario=request.user)
    seguidos = perfil_usuario.seguidos.all()
    publicaciones = Publicacion.objects.filter(autor__in=[seguido.usuario for seguido in seguidos])
    publicaciones_propias = Publicacion.objects.filter(autor=request.user)
    publicaciones = publicaciones | publicaciones_propias
    if not publicaciones.exists():
        publicaciones = None
    return render(request, 'lista_publicaciones.html', {'publicaciones': publicaciones})



def action_view(request, action_id):
    action = Action.objects.get(id=action_id)
    if request.user.is_authenticated:
        update_user_points(request.user.id, action_id, action.points)
    return render(request, 'action.html', {'action': action})

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
        
        Concurso.objects.create(
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
    # Ordenar por ranking y tomar el primero
    ganador = PerfilUsuario.objects.order_by('-puntos').first()
    usuario= User.objects.get(id=ganador.usuario_id)
    top_usuarios = PerfilUsuario.objects.order_by('-puntos')[:10]
    return render(request, 'concurso_resultados.html', {
        'concurso': concurso_actual,
        'ganador': ganador,
        'usuario':usuario,
        'top_usuarios':top_usuarios,
    })
    

def lista_comunidades(request):
    comunidades_activas = Comunidad.objects.filter(activada=True)
    return render(request, 'lista_comunidades.html', {'comunidades': comunidades_activas})




@login_required
def detalle_campaign(request, pk):
    campaign = get_object_or_404(Campaign, pk=pk)
    desafio=campaign.desafio
    
    if request.method == 'POST' and campaign.activa:
        respuesta_form = RespuestaForm(request.POST)
        if respuesta_form.is_valid():
            respuesta = respuesta_form.save(commit=False)
            respuesta.autor = request.user
            respuesta.campaign = campaign
            respuesta.save()
            
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='responder_campaign',
                puntos_ganados=20
            )
            accion: Action | None= Action.objects.filter(name='responder_campaign').first()
            update_user_points(request.user.id, accion.id, accion.points)
            
            return redirect('detalle_campaign', pk=campaign.pk)
    else:
        respuesta_form = RespuestaForm()
    
    puntuaciones = Action.objects.filter(name__startswith='puntos')
    
    return render(request, 'detalle_campaign.html', {
        'campaign': campaign,
        'respuesta_form': respuesta_form,
        'puntuaciones': puntuaciones,
        'is_creador': request.user == campaign.desafio.creador,
        'campaign_activa': campaign.activa,
        'puntos':desafio.puntaje
    })

@login_required
def lista_campaigns(request):
    campaigns = Campaign.objects.all().order_by('-id')
    filtro = request.GET.get('filtro', 'todas')
    
    if filtro == 'activas':
        campaigns = campaigns.filter(activa=True)
    elif filtro == 'no_activas':
        campaigns = campaigns.filter(activa=False)
    
    return render(request, 'lista_campaigns.html', {
        'campaigns': campaigns,
        'filtro_actual': filtro
    })
    
@login_required
def puntuar_respuesta(request, pk, estrellas):
    respuesta = get_object_or_404(Respuesta, pk=pk)
    if request.method == 'POST' and request.user == respuesta.campaign.desafio.creador:
        respuesta.puntuacion = int(estrellas)
        respuesta.save()
        return JsonResponse({'status': 'success', 'puntuacion': respuesta.puntuacion})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def guardar_donacion(request,pk):
    if request.method == 'POST':
        nombre = request.POST['nombre']
        identificador_transferencia = request.POST['identificador_transferencia']
        cantidad = request.POST['cantidad']
        desafio= Desafio.objects.get(id=pk)
        # Aquí deberías validar los datos antes de guardarlos
        # Por ejemplo:
        desafio.cantidad_donada+=Decimal(cantidad)
        if (float(cantidad)<desafio.min_monto or float(cantidad)>desafio.max_monto or desafio.cantidad_donada>desafio.objetivo_monto):
            return render(request, 'crear_donacion.html', {'error': 'Por favor, el mnto debe ser entre {desafio.min_monto} y {desafio.max_monto}'})
        desafio.save()
        # Guardar la donación en la base de datos
        DonacionComunidad.objects.create(
            nombre=nombre,
            identificador_transferencia=identificador_transferencia,
            cantidad=cantidad,
        )
        
        # Si todo salió bien, redirige al usuario a la lista de donaciones
        return redirect('inicio')
    qr = Cuenta.objects.first()
    # Si es una solicitud GET, muestra el formulario vacío con los datos del usuario prellenados
    form = DonacionComunidadForm(initial={
        'nombre': f"{request.user.first_name} {request.user.last_name}",
        'identificador_transferencia': '',
        'cantidad': ''
    })
    
    return render(request, 'crear_donacion.html', {'form': form,'qr':qr})


@login_required
def chat_comunidad(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)
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
        perfil_form = EditUserProfileForm(request.POST, request.FILES, instance=perfil_usuario)
        user_form = EditUserForm(request.POST, instance=user)
        
        if perfil_form.is_valid() and user_form.is_valid():
            perfil_form.save()
            user_form.save()
    else:
        perfil_form = EditUserProfileForm(instance=perfil_usuario)
        user_form = EditUserForm(instance=user)
    
    return render(request, 'editar_perfil.html', {
        'form_perfil': perfil_form,
        'form_usuario': user_form,
        'user': user,
    })
    
@login_required
def unirse_comunidad(request, pk):
    comunidad = Comunidad.objects.get(pk=pk)
    if comunidad.publica:
        comunidad.miembros.add(request.user)
        print(f"El usuario {request.user.username} se unió a la comunidad {comunidad.nombre}")
        return redirect('detalle_comunidad', pk=pk)
    else:
        return redirect('detalle_comunidad', pk=pk)
    
@login_required
def salir_comunidad(request, pk):
    comunidad = Comunidad.objects.get(pk=pk)
    comunidad.miembros.remove(request.user)
    print("salio")
    return redirect('detalle_comunidad', pk=pk)

@login_required
def solicitar_membresia(request, comunidad_id):
    comunidad = get_object_or_404(Comunidad, id=comunidad_id)

    if request.method == 'POST':
        # Verificar que la comunidad es privada
        if comunidad.publica:
            return redirect('detalle_comunidad', comunidad_id=comunidad_id)

        # Crear la solicitud de membresía
        solicitud, created = SolicitudMembresia.objects.get_or_create(comunidad=comunidad, usuario=request.user)
        if created:
            # Notificar que la solicitud fue enviada
            return redirect('detalle_comunidad', comunidad_id)
        else:
            # Si ya existe una solicitud pendiente
            return render(request, 'solicitud_existente.html', {'comunidad': comunidad})

    return render(request, 'solicitud_membresia.html', {'comunidad': comunidad})

def ranking_usuarios(request):
    ranking = []
    form = RangoFechaForm(request.POST or None)

    # Definir un rango de fechas predeterminado si no se proporciona
    if request.method == 'POST' and form.is_valid():
        fecha_inicio = form.cleaned_data['fecha_inicio']
        fecha_fin = form.cleaned_data['fecha_fin']
    else:
        # Establecer un rango de fechas predeterminado (por ejemplo, los últimos 30 días)
        fecha_fin = timezone.now()
        fecha_inicio = fecha_fin - timedelta(days=30)

    # Obtener el ranking de usuarios en base al rango de fechas
    ranking = (
        ActividadUsuario.objects.filter(
            fecha_hora__range=(fecha_inicio, fecha_fin)
        )
        .values('usuario__username')
        .annotate(total_puntos=Sum('puntos_ganados'))
        .order_by('-total_puntos')
    )

    return render(request, 'ranking.html', {'ranking': ranking, 'form': form})