# Generated by Django 5.0.2 on 2024-03-18 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orimgasapp', '0008_remove_priesgiasrinesinstrukcijos_instruktavimo_tipas_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='mokymai',
            name='slug',
            field=models.SlugField(default=1, unique=True),
            preserve_default=False,
        ),
    ]