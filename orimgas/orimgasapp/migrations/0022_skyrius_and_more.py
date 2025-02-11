# Generated by Django 5.0.2 on 2025-01-26 15:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0021_alter_asmeninesapsaugospriemones_pavadinimas_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Skyrius',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=10000, verbose_name='pavadinimas')),
            ],
        ),
        migrations.AlterField(
            model_name='asmeninesapsaugospriemones',
            name='periodiskumas',
            field=models.SmallIntegerField(choices=[(6, '6 mėnesiai'), (12, '12 mėnesių'), (24, '24 mėnesiai'), (36, '36 mėnesiai'), (60, '60 mėnesių')], default=6, verbose_name='periodicity'),
        ),
        migrations.AddField(
            model_name='company',
            name='skyrius',
            field=models.ManyToManyField(blank=True, default=None, related_name='company', to='orimgasapp.skyrius'),
        ),
    ]
