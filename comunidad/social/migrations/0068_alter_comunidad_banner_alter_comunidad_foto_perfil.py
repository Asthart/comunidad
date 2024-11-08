# Generated by Django 4.2.16 on 2024-11-03 05:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0067_remove_comunidad_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comunidad',
            name='banner',
            field=models.ImageField(blank=True, default='comunidades/banners/banner_default.jpg', null=True, upload_to='comunidades/banners/'),
        ),
        migrations.AlterField(
            model_name='comunidad',
            name='foto_perfil',
            field=models.ImageField(blank=True, default='comunidades/perfiles/perfil_default.jpg', null=True, upload_to='comunidades/perfiles/'),
        ),
    ]