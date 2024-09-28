# Generated by Django 4.2.16 on 2024-09-28 01:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('social', '0031_remove_desafio_max_donaciones_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voto',
            name='es_positivo',
        ),
        migrations.AddField(
            model_name='voto',
            name='puntuacion',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='desafio',
            name='objetivo_monto',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]