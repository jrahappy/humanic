# Generated by Django 5.1 on 2024-09-20 04:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0014_alter_uploadhistory_afile'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmaster',
            name='adjusted_price',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='reportmaster',
            name='applied_rate',
            field=models.FloatField(blank=True, default=0, null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(1.0)]),
        ),
        migrations.AddField(
            model_name='reportmaster',
            name='is_completed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='reportmaster',
            name='is_onsite',
            field=models.BooleanField(default=False),
        ),
    ]