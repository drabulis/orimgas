# Generated by Django 5.0.2 on 2025-04-03 04:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_remove_user_skyrius_user_skyrius'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='kalba',
            field=models.SmallIntegerField(choices=[(1, 'LT'), (2, 'RU'), (3, 'EN')], default=1, verbose_name='kalba'),
        ),
    ]
