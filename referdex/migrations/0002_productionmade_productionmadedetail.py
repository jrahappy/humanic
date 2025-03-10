# Generated by Django 5.1 on 2024-11-17 04:38

import django.db.models.deletion
import utils.base_func
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0015_company_customuser'),
        ('referdex', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductionMade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('specialty2', models.CharField(blank=True, choices=utils.base_func.get_specialty_choices, max_length=30, null=True)),
                ('modality', models.CharField(blank=True, choices=utils.base_func.get_amodality_choices, max_length=10, null=True)),
                ('requested_qty', models.IntegerField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('referrals', models.CharField(blank=True, max_length=250, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='customer.company')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProductionMadeDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('assigned_qty', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('production', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='referdex.productionmade')),
                ('provider', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
