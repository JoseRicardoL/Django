# Generated by Django 2.0.5 on 2018-05-30 12:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Administrador',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Descripcion', models.CharField(max_length=120)),
                ('Telefono', models.IntegerField()),
                ('Imagen', sorl.thumbnail.fields.ImageField(upload_to='Administradores')),
                ('Administrador', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Administrador',
                'verbose_name_plural': 'Administradores',
            },
        ),
    ]
