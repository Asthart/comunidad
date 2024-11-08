# Generated by Django 4.2.16 on 2024-11-03 05:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0068_alter_comunidad_banner_alter_comunidad_foto_perfil'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comunidad',
            name='crowuser',
        ),
        migrations.CreateModel(
            name='SolicitudCrowuser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_solicitud', models.DateTimeField(auto_now_add=True)),
                ('estado', models.CharField(choices=[('pendiente', 'Pendiente'), ('aceptada', 'Aceptada'), ('rechazada', 'Rechazada')], default='pendiente', max_length=10)),
                ('comunidad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.comunidad')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='comunidad',
            name='crowuser',
            field=models.ManyToManyField(related_name='comunidades_crowuser', to=settings.AUTH_USER_MODEL),
        ),
    ]