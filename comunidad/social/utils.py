import requests
from .models import *
from django.utils.timezone import now
from django.db.models import F
def get_clasificacion(puntos):
    clasificaciones = Clasificacion.objects.all().order_by('-umbral_puntos')
    print(f"Puntos {clasificaciones} sigue a ")
    for clasificacion in clasificaciones:
        if puntos >= clasificacion.umbral_puntos:
            return clasificacion.nombre
    return 'Novato'

def update_user_points(user_id, action_id, points):
    user = User.objects.get(id=user_id)
    action = Accion.objects.get(id=action_id)
    if not points==0:
        # Actualizar puntos totales del perfil del usuario
        PerfilUsuario.objects.filter(usuario_id=user.id).update(puntos=F('puntos') + points)
    
        # Crear registro de acción
        AccionUsuario.objects.create(
            user=user,
            accion=action,
            timestamp=now(),
            puntos=points
        )
    
import datetime

def calcular_ganador():
    # Logica para calcular el ganador basado en el ranking individual
    # Por ejemplo:
    concurso_actual = Concurso.objects.latest('fecha_fin')
    # Ordenar por ranking y tomar el primero
    ganador = PerfilUsuario.objects.order_by('-puntos').first()
    
    if ganador:
        ResultadoConcurso.objects.create(
            concurso=concurso_actual,
            ganador=ganador.usuario,
            fecha_resultado=datetime.date.today()
        )
        print(f"El ganador del concurso '{concurso_actual.nombre}' es {ganador.usuario.username}")
    else:
        print("No se pudo determinar un ganador")

def validate_session_with_external_app(sessionid):
    response = requests.get('https://external.example.com/api/validate_session', params={'sessionid': sessionid})

    if response.status_code == 200:
        user_info = response.json()
        # Aquí puedes buscar o crear el usuario en tu base de datos
        user, created = User.objects.get_or_create(username=user_info['username'], defaults={
            'email': user_info['email'],
            'first_name': user_info['first_name'],
            'last_name': user_info['last_name'],
        })
        return user

    return None

def is_first_visit(request, url):
    return not FirstVisit.objects.filter(user=request.user, url=url).exists()