# Generated by Django 4.2.16 on 2024-09-30 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0041_merge_20240929_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publicacion',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='publicaciones/imagenes/'),
        ),
    ]
