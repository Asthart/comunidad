from .models import Action, Clasificacion, PerfilUsuario, UserAction, User
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