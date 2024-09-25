from .models import Action, Clasificacion, Concurso, PerfilUsuario, ResultadoConcurso, UserAction, User
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
    action = Action.objects.get(id=action_id)
    
    # Actualizar puntos totales del perfil del usuario
    PerfilUsuario.objects.filter(usuario_id=user.id).update(puntos=F('puntos') + points)
    
    # Crear registro de acción
    UserAction.objects.create(
        user=user,
        action=action,
        timestamp=now()
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

# Ejecuta esta función periódicamente (por ejemplo, cada hora)
#import schedule
#import time

#def job():
 #   calcular_ganador()

#schedule.every().hour.do(job)

#while True:
#    schedule.run_pending()
#    time.sleep(60)
