# Generated by Django 4.2.16 on 2024-11-04 01:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0073_remove_solicitudcrowuser_comunidad_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='solicitudcrowuser',
            name='estado',
        ),
    ]