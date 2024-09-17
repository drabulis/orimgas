# Generated by Django 5.0.2 on 2024-09-03 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0010_user_civiline_sauga'),
        ('orimgasapp', '0019_asmeninesapsaugospriemones_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='AsmeninesApsaugosPriemones',
            field=models.ManyToManyField(blank=True, default=None, related_name='users', to='orimgasapp.asmeninesapsaugospriemones', verbose_name='AsmeninesApsaugosPriemones'),
        ),
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(max_length=100, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(max_length=100, verbose_name='last name'),
        ),
        migrations.AlterField(
            model_name='user',
            name='med_patikros_periodas',
            field=models.SmallIntegerField(choices=[(12, '12 Mėnesių'), (24, '24 Mėnesiai')], default=12, verbose_name='med patikros periodas'),
        ),
    ]