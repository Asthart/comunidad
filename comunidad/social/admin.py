# admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Comunidad, Proyecto, Desafio, PerfilUsuario, MensajeChat, ActividadUsuario, Publicacion, Tag

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
    list_display = ('emisor', 'receptor', 'contenido', 'fecha_hora')
    list_filter = ('fecha_hora',)
    search_fields = ('emisor__username', 'receptor__username', 'contenido')

@admin.register(ActividadUsuario)
class ActividadUsuarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo_actividad', 'fecha_hora', 'puntos_ganados')
    list_filter = ('tipo_actividad', 'fecha_hora')
    search_fields = ('usuario__username', 'tipo_actividad')
    
@admin.register(Publicacion)
class ActividadUsuarioAdmin(admin.ModelAdmin):
    list_display = ('autor',)
    list_filter = ('autor',)
    search_fields = ('autor',)
    
admin.site.register(Tag)