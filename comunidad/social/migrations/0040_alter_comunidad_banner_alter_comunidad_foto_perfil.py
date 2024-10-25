# Generated by Django 4.2.16 on 2024-09-29 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0039_merge_0037_mensajechatcomunidad_0038_cuenta'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comunidad',
            name='banner',
            field=models.ImageField(blank=True, default='static/images/backgroud1.jpg', null=True, upload_to='comunidades/banners/'),
        ),
        migrations.AlterField(
            model_name='comunidad',
            name='foto_perfil',
            field=models.ImageField(blank=True, default='static/images/default-avatar.svg', null=True, upload_to='comunidades/perfiles/'),
        ),
    ]
