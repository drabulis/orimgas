# Generated by Django 5.0.2 on 2024-02-29 15:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0005_testai_priesgiasrinesinstrukcijos_mokymai_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='instruction',
            name='periodiskumas',
            field=models.IntegerField(blank=True, default=365, null=True, verbose_name='periodicity'),
        ),
        migrations.CreateModel(
            name='KitiDokumentai',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=100)),
                ('pdf', models.FileField(upload_to='kiti_dokumentai')),
                ('imone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kiti_dokumentai', to='orimgasapp.company', verbose_name='company')),
            ],
        ),
        migrations.CreateModel(
            name='KituDocPasirasymas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'not signed'), (1, 'signed')], default=0, verbose_name='status')),
                ('date_signed', models.DateField(blank=True, default=None, null=True, verbose_name='date signed')),
                ('next_sign', models.DateField(blank=True, default=None, null=True, verbose_name='next sign')),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orimgasapp.kitidokumentai', verbose_name='instruction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='MokymuPasirasymas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'not signed'), (1, 'signed')], default=0, verbose_name='status')),
                ('date_signed', models.DateField(blank=True, default=None, null=True, verbose_name='date signed')),
                ('next_sign', models.DateField(blank=True, default=None, null=True, verbose_name='next sign')),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orimgasapp.mokymai', verbose_name='instruction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
        migrations.CreateModel(
            name='PriesgaisriniuPasirasymas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'not signed'), (1, 'signed')], default=0, verbose_name='status')),
                ('date_signed', models.DateField(blank=True, default=None, null=True, verbose_name='date signed')),
                ('next_sign', models.DateField(blank=True, default=None, null=True, verbose_name='next sign')),
                ('instruction', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orimgasapp.priesgiasrinesinstrukcijos', verbose_name='instruction')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
        ),
    ]