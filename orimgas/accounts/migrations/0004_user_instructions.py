# Generated by Django 4.2.7 on 2023-11-15 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0001_initial'),
        ('accounts', '0003_user_is_supervisor'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='instructions',
            field=models.ManyToManyField(blank=True, default=None, related_name='users', to='orimgasapp.instruction', verbose_name='instructions'),
        ),
    ]