# Generated by Django 5.0.2 on 2025-01-26 15:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_user_skyrius'),
        ('orimgasapp', '0023_remove_company_skyrius_skyrius_company'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='skyrius',
        ),
        migrations.AddField(
            model_name='user',
            name='skyrius',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='users', to='orimgasapp.skyrius', verbose_name='Skyrius'),
        ),
    ]
