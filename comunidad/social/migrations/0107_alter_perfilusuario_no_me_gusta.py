# Generated by Django 4.2.16 on 2024-12-02 01:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0106_alter_accion_options_alter_clasificacion_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='perfilusuario',
            name='no_me_gusta',
            field=models.ManyToManyField(to='social.tematica'),
        ),
    ]