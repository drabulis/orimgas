# Generated by Django 4.2.7 on 2023-11-15 06:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_supervisor',
            field=models.BooleanField(default=False),
        ),
    ]