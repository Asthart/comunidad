# Generated by Django 4.2.16 on 2024-10-27 17:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0062_remove_respuesta_puntuacion_respuesta_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='comunidad',
            name='crowuser',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
