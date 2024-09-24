from .models import Clasificacion

def get_clasificacion(puntos):
    clasificaciones = Clasificacion.objects.all().order_by('-umbral_puntos')
    print(f"Puntos {clasificaciones} sigue a ")
    for clasificacion in clasificaciones:
        if puntos >= clasificacion.umbral_puntos:
            return clasificacion.nombre
    return 'Novato'