# Generated by Django 4.2.16 on 2024-11-27 02:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0096_comunidad_tags'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comunidad',
            old_name='tags',
            new_name='tematica',
        ),
    ]
