# admin.py

import os
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.urls import path
from .models import *
from django.core.mail import send_mail
class PerfilUsuarioInline(admin.StackedInline):
    model = PerfilUsuario
    can_delete = False
    verbose_name_plural = 'Perfil de Usuario'

class CustomUserAdmin(UserAdmin):
    inlines = (PerfilUsuarioInline,)

admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Campaign)

@admin.register(Comunidad)
class ComunidadAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'administrador','activada')
    search_fields = ('nombre', 'administrador__username')
    filter_horizontal = ('miembros',)
    
    def Activar(self, request, queryset):
        updated = queryset.update(activada=True)
        if updated:
            self.send_activation_email(queryset.first())
        return updated

    def send_activation_email(self, comunidad):
        subject = 'Tu comunidad ha sido activada'
        message = f'Hola {comunidad.administrador.username},\n\n' \
                  f'Tu comunidad "{comunidad.nombre}" ha sido activada.\n\n' \
                  
        ADMIN_EMAIL = os.environ.get('EMAIL_HOST_USER')
        send_mail(
            subject,
            message,
            ADMIN_EMAIL,  # Reemplaza con tu dirección de correo
            [comunidad.administrador.email],
            fail_silently=False,
        )
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(administrador=request.user)
        
    actions = ['Activar']  # Agregar esta línea

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['actions_on_top'] = True
        return super().changelist_view(request, extra_context=extra_context)

    def get_actions(self, request):
        actions = super().get_actions(request)
        
        try:
            del actions['delete_selected']
        except KeyError:
            pass
        
        return actions
    
@admin.register(Proyecto)
class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'comunidad', 'fecha_creacion')
    list_filter = ('comunidad', 'fecha_creacion')
    search_fields = ('titulo', 'creador__username', 'comunidad__nombre')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(comunidad__administrador=request.user)

@admin.register(Desafio)
class DesafioAdmin(admin.ModelAdmin):
    list_display = ('id','titulo', 'creador', 'comunidad', 'fecha_inicio', 'fecha_fin')
    list_filter = ('comunidad', 'fecha_inicio', 'fecha_fin')
    search_fields = ('titulo', 'creador__username', 'comunidad__nombre')
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(comunidad__administrador=request.user)

@admin.register(MensajeChat)
class MensajeChatAdmin(admin.ModelAdmin):
    list_display = ('emisor', 'room_name', 'contenido', 'fecha_envio', 'leido', 'fecha_lectura')
    list_filter = ('emisor', 'fecha_envio', 'leido')
    search_fields = ('emisor__username', 'room_name', 'contenido')
    date_hierarchy = 'fecha_envio'


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
    
@admin.register(UserAction)
class UserActionAdmin(admin.ModelAdmin):
    list_display = ('user','accion','timestamp','puntos')
    search_fields = ('nombre',)

@admin.register(Concurso)
class ConcursoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion', 'fecha_inicio', 'fecha_fin', 'premio')
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
    
@admin.register(DonacionComunidad)
class DonacionComunidadAdmin(admin.ModelAdmin):
    list_display = ('id','nombre', 'identificador_transferencia','cantidad')
    search_fields = ('cantidad',)
    
@admin.register(Cuenta)
class CuentaAdmin(admin.ModelAdmin):
    list_display = ('id','qr_code', 'numero_cuenta')


@admin.register(MensajeChatComunidad)
class MensajeChatComunidadAdmin(admin.ModelAdmin):
    list_display = ('emisor', 'comunidad', 'contenido_truncado', 'fecha_envio')
    list_filter = ('comunidad', 'fecha_envio')
    search_fields = ('emisor__username', 'comunidad__nombre', 'contenido')
    actions = ['delete_selected']

    def contenido_truncado(self, obj):
        return obj.contenido[:50] + '...' if len(obj.contenido) > 50 else obj.contenido
    contenido_truncado.short_description = 'Contenido'



class SolicitudMembresiaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'comunidad', 'fecha_solicitud', 'estado')
    list_filter = ('estado',)
    actions = ['aceptar_solicitud', 'rechazar_solicitud']

    def aceptar_solicitud(self, request, queryset):
        for solicitud in queryset:
            # Cambiar el estado de la solicitud a 'aceptada'
            solicitud.estado = 'aceptada'
            # Agregar el usuario a la comunidad
            #solicitud.comunidad.miembros.add(solicitud.usuario)
            comunidad = solicitud.comunidad
            print(comunidad)
            nuevo_miembro = solicitud.usuario
            comunidad.miembros.add(nuevo_miembro)
            solicitud.save()  # Guardar los cambios en la solicitud
            solicitud.delete()
        self.message_user(request, "Las solicitudes seleccionadas han sido aceptadas y los usuarios han sido añadidos a la comunidad.")

    def rechazar_solicitud(self, request, queryset):
        for solicitud in queryset:
            # Cambiar el estado de la solicitud a 'rechazada'
            solicitud.estado = 'rechazada'
            solicitud.save()  # Guardar los cambios en la solicitud
            solicitud.delete()
        self.message_user(request, "Las solicitudes seleccionadas han sido rechazadas.")

    aceptar_solicitud.short_description = "Aceptar solicitudes seleccionadas"
    rechazar_solicitud.short_description = "Rechazar solicitudes seleccionadas"

admin.site.register(SolicitudMembresia, SolicitudMembresiaAdmin)
