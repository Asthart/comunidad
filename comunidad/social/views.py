# views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Comunidad, Proyecto, Desafio, PerfilUsuario, MensajeChat, ActividadUsuario
from .forms import ComunidadForm, ProyectoForm, DesafioForm
from django.contrib.auth.models import User
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
@permission_required('tu_app.add_comunidad', raise_exception=True)
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

@login_required
@permission_required('tu_app.add_proyecto', raise_exception=True)
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
@permission_required('tu_app.add_desafio', raise_exception=True)
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
    mensajes = MensajeChat.objects.filter(
        Q(emisor=request.user, receptor=receptor) |
        Q(emisor=receptor, receptor=request.user)
    ).order_by('fecha_hora')
    
    if request.method == 'POST':
        contenido = request.POST.get('contenido')
        MensajeChat.objects.create(
            emisor=request.user,
            receptor=receptor,
            contenido=contenido
        )
        return redirect('chat', receptor_id=receptor_id)
    
    return render(request, 'chat.html', {'receptor': receptor, 'mensajes': mensajes})

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
            user = form.save()
            login(request, user)
            return redirect('inicio')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})