# Generated by Django 4.2.16 on 2024-09-30 23:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0043_desafio_puntaje'),
    ]

    operations = [
        migrations.CreateModel(
            name='PuntajeDesafio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puntaje', models.PositiveIntegerField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('desafio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puntajes', to='social.desafio')),
                ('usuario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('desafio', 'usuario')},
            },
        ),
    ]