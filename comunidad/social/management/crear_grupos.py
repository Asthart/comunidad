# management/commands/crear_grupos.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from social.models import Comunidad, Proyecto, Desafio

class Command(BaseCommand):
    help = 'Crea grupos predefinidos con permisos específicos'

    def handle(self, *args, **options):
        # Grupo de Administradores
        admin_group, created = Group.objects.get_or_create(name='Administradores')
        admin_permissions = Permission.objects.all()
        admin_group.permissions.set(admin_permissions)

        # Grupo de Moderadores
        mod_group, created = Group.objects.get_or_create(name='Moderadores')
        mod_permissions = Permission.objects.filter(
            content_type__in=[
                ContentType.objects.get_for_model(Comunidad),
                ContentType.objects.get_for_model(Proyecto),
                ContentType.objects.get_for_model(Desafio)
            ]
        )
        mod_group.permissions.set(mod_permissions)

        # Grupo de Usuarios Regulares
        user_group, created = Group.objects.get_or_create(name='Usuarios Regulares')
        user_permissions = Permission.objects.filter(
            codename__in=['add_proyecto', 'change_proyecto', 'view_proyecto',
                          'add_desafio', 'change_desafio', 'view_desafio']
        )
        user_group.permissions.set(user_permissions)

        self.stdout.write(self.style.SUCCESS('Grupos y permisos creados exitosamente'))