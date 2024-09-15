# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q

from comunidad.social.decorators import permiso_requerido
from .models import Comunidad, Proyecto, Desafio, PerfilUsuario, MensajeChat, ActividadUsuario, User
from .forms import ArchivoProyectoForm, ComunidadForm, ProyectoForm, DesafioForm
from django.contrib.auth.models import User

def registrar(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            PerfilUsuario.objects.create(usuario=usuario)
            login(request, usuario)
            return redirect('inicio')
    else:
        form = UserCreationForm()
    return render(request, 'registrar.html', {'form': form})

@login_required
def inicio(request):
    comunidades = Comunidad.objects.filter(miembros=request.user)
    proyectos = Proyecto.objects.filter(comunidad__in=comunidades)
    desafios = Desafio.objects.filter(comunidad__in=comunidades)
    return render(request, 'inicio.html', {
        'comunidades': comunidades,
        'proyectos': proyectos,
        'desafios': desafios
    })

@login_required
@permiso_requerido('crear_comunidad')
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
            return redirect('detalle_comunidad', pk=comunidad.pk)
    else:
        form = ComunidadForm()
    return render(request, 'crear_comunidad.html', {'form': form})

@login_required
def detalle_comunidad(request, pk):
    comunidad = get_object_or_404(Comunidad, pk=pk)
    proyectos = Proyecto.objects.filter(comunidad=comunidad)
    desafios = Desafio.objects.filter(comunidad=comunidad)
    es_admin = comunidad.administrador == request.user
    return render(request, 'detalle_comunidad.html', {
        'comunidad': comunidad,
        'proyectos': proyectos,
        'desafios': desafios,
        'es_admin': es_admin
    })

# views.py

@login_required
@permiso_requerido('crear_proyecto')
def crear_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)
        archivo_form = ArchivoProyectoForm(request.POST, request.FILES)
        if form.is_valid() and archivo_form.is_valid():
            proyecto = form.save(commit=False)
            proyecto.creador = request.user
            proyecto.save()
            
            archivo = archivo_form.save(commit=False)
            archivo.subido_por = request.user
            archivo.save()
            
            proyecto.archivos.add(archivo)
            
            ActividadUsuario.objects.create(
                usuario=request.user,
                tipo_actividad='crear_proyecto',
                puntos_ganados=30
            )
            return redirect('detalle_proyecto', pk=proyecto.pk)
    else:
        form = ProyectoForm()
        archivo_form = ArchivoProyectoForm()
    return render(request, 'crear_proyecto.html', {'form': form, 'archivo_form': archivo_form})

@login_required
def detalle_proyecto(request, pk):
    proyecto = get_object_or_404(Proyecto, pk=pk)
    return render(request, 'detalle_proyecto.html', {'proyecto': proyecto})

@login_required
@permiso_requerido('crear_desafio')
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
    
# views.py

@login_required
def chat(request, receptor_id):
    receptor = get_object_or_404(User, id=receptor_id)
    mensajes = MensajeChat.objects.filter(
        Q(emisor=request.user, receptor=receptor) |
        Q(emisor=receptor, receptor=request.user)
    ).order_by('fecha_hora')
    
    return render(request, 'chat.html', {
        'receptor': receptor,
        'mensajes': mensajes,
        'room_name': f'{request.user.id}_{receptor.id}'
    })
