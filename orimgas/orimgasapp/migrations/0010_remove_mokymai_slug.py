# Generated by Django 5.0.2 on 2024-03-18 16:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0009_mokymai_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mokymai',
            name='slug',
        ),
    ]
