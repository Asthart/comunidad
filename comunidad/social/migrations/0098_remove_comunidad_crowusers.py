# Generated by Django 4.2.16 on 2024-11-27 02:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0097_rename_tags_comunidad_tematica'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comunidad',
            name='crowusers',
        ),
    ]
