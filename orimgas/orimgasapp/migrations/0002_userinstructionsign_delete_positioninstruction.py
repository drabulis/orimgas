# Generated by Django 4.2.7 on 2023-11-17 07:43

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orimgasapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserInstructionSign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'not signed'), (1, 'signed')], default=0, verbose_name='status')),
                ('date_signed', models.DateField(blank=True, default=None, null=True, verbose_name='date signed')),
                ('next_sign', models.DateField(blank=True, default=None, null=True, verbose_name='next sign')),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orimgasapp.instruction', verbose_name='instruction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.DeleteModel(
            name='PositionInstruction',
        ),
    ]
