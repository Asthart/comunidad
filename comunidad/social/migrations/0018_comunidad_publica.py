# Generated by Django 3.2.10 on 2024-09-25 02:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0017_auto_20240924_2126'),
    ]

    operations = [
        migrations.AddField(
            model_name='comunidad',
            name='publica',
            field=models.BooleanField(default=False),
        ),
    ]
