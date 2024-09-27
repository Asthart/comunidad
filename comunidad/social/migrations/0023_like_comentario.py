# Generated by Django 4.2.16 on 2024-09-27 02:57

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('social', '0022_like_comentario'),
    ]

    operations = [
        migrations.CreateModel(
            name='Like_Comentario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha_like', models.DateTimeField(auto_now_add=True)),
                ('autor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('comentario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='social.comentario')),
            ],
        ),
    ]
