# Generated by Django 3.2.10 on 2024-09-25 00:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0016_alter_action_points'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('activa', models.BooleanField(default=False)),
                ('desafio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='social.desafio')),
            ],
        ),
        migrations.CreateModel(
            name='Respuesta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('respuesta', models.CharField(max_length=300)),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.campaign')),
            ],
        ),
        migrations.CreateModel(
            name='AdjuntoRespuesta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='respuestas/archivos/')),
                ('respuesta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='adjuntos', to='social.respuesta')),
            ],
        ),
    ]
