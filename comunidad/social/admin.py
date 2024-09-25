# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path
from .models import Action, Clasificacion, Comunidad, Concurso, Premio, Proyecto, Desafio, PerfilUsuario, MensajeChat, ActividadUsuario, Publicacion, Tag,TerminosCondiciones

class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'administrador')
    search_fields = ('nombre', 'administrador__username')
    filter_horizontal = ('miembros',)

@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'comunidad', 'fecha_creacion')
    list_filter = ('comunidad', 'fecha_creacion')
    search_fields = ('titulo', 'creador__username', 'comunidad__nombre')

@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'comunidad', 'fecha_inicio', 'fecha_fin')
    list_filter = ('comunidad', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'creador__username', 'comunidad__nombre')

@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display = ('emisor', 'room_name', 'contenido', 'fecha_envio', 'leido', 'fecha_lectura')
    list_filter = ('emisor', 'fecha_envio', 'leido')
    search_fields = ('emisor__username', 'room_name', 'contenido')
    date_hierarchy = 'fecha_envio'

@admin.register(ActividadUsuario)
class ActividadUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_actividad', 'fecha_hora', 'puntos_ganados')
    list_filter = ('tipo_actividad', 'fecha_hora')
    search_fields = ('usuario__username', 'tipo_actividad')
    
admin.site.register(Tag)

'''
<small class="message-time">
                    (Enviado: {{ mensaje.fecha_envio|date:"d/m/Y H:i:s" }})
                    <span class="read-status">
                        {% if mensaje.leido %}
                            (Leído: {{ mensaje.fecha_lectura|date:"d/m/Y H:i:s" }})
                        {% endif %}
                    </span>
                </small>
'''

admin.site.register(TerminosCondiciones)

@admin.register(Clasificacion)
class ClasificacionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'umbral_puntos')
    search_fields = ('nombre',)
    
@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('id','name', 'points')
    search_fields = ('name',)
    
@admin.register(Premio)
class PremioAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    

@admin.register(Concurso)
class ConcursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'fecha_inicio', 'fecha_fin', 'premio')
    list_filter = ['fecha_inicio', 'fecha_fin']
    search_fields = ['nombre']
    
    class Media:
        css = {
            'all': ('css/styles.css',)
        }





    def concurso_resultados(self, request):
        # Aquí irá la lógica para mostrar los resultados del concurso actual
        # Por ahora, solo mostraremos un mensaje
        return HttpResponse("Resultados del concurso actual")
