# Generated by Django 4.2.7 on 2023-12-31 17:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0003_remove_instruction_periodity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instruction',
            name='periodiskumas',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='periodicity'),
        ),
    ]
