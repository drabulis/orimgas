# Generated by Django 5.0.2 on 2024-02-26 14:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0004_alter_instruction_periodiskumas'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testai',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='PriesgiasrinesInstrukcijos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=100)),
                ('periodiskumas', models.IntegerField(blank=True, default=365, null=True, verbose_name='periodicity')),
                ('pdf', models.FileField(upload_to='priesgaisrines_instrukcijos')),
                ('imone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='priesgiasrines_instrukcijos', to='orimgasapp.company', verbose_name='company')),
                ('testas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='priesgiasrines_instrukcijos', to='orimgasapp.testai', verbose_name='test')),
            ],
        ),
        migrations.CreateModel(
            name='Mokymai',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pavadinimas', models.CharField(max_length=100)),
                ('periodiskumas', models.IntegerField(blank=True, default=365, null=True, verbose_name='periodicity')),
                ('pdf', models.FileField(upload_to='mokymai')),
                ('imone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mokymai', to='orimgasapp.company', verbose_name='company')),
                ('testas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mokymai', to='orimgasapp.testai', verbose_name='test')),
            ],
        ),
        migrations.CreateModel(
            name='TestoKlausimas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('klausimas', models.CharField(max_length=100)),
                ('testas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='klausimai', to='orimgasapp.testai', verbose_name='test')),
            ],
        ),
        migrations.CreateModel(
            name='TestoAtsakymas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('atsakymas', models.CharField(max_length=100)),
                ('teisingas', models.BooleanField(default=False)),
                ('klausimas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='atsakymai', to='orimgasapp.testoklausimas', verbose_name='answer')),
            ],
        ),
    ]
