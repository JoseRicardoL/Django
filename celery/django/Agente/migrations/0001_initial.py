# Generated by Django 2.0.5 on 2018-05-13 18:36

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Agente',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('NombreHost', models.CharField(max_length=120)),
                ('Ip', models.CharField(max_length=120)),
                ('Ip_publica', models.CharField(max_length=120)),
                ('Protocolo', models.PositiveIntegerField(choices=[(1, 'v1'), (2, 'v2c'), (3, 'v3')])),
                ('Puerto', models.IntegerField()),
                ('Comunidad', models.CharField(max_length=120)),
                ('Administrador_Agente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Agentes',
                'verbose_name': 'Agente',
            },
        ),
    ]