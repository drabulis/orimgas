# Generated by Django 5.0.2 on 2025-01-26 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_user_asmeninesapsaugospriemones_and_more'),
        ('orimgasapp', '0022_skyrius_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='skyrius',
            field=models.ManyToManyField(blank=True, default=None, related_name='users', to='orimgasapp.skyrius', verbose_name='Skyrius'),
        ),
    ]
