# Generated by Django 5.1 on 2024-09-14 13:06

import django.db.models.deletion
import utils.base_func
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0002_company_clinic_id'),
        ('minibooks', '0006_reportmaster_unverified_message_and_more'),
        ('product', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='uploadhistory',
            name='aggregated',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='uploadhistory',
            name='is_deleted',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.AddField(
            model_name='uploadhistory',
            name='verified',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
        migrations.CreateModel(
            name='ReportMasterStat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ayear', models.CharField(max_length=4, verbose_name='년도')),
                ('amonth', models.CharField(max_length=2, verbose_name='월')),
                ('aday', models.CharField(blank=True, max_length=2, null=True)),
                ('amodality', models.CharField(choices=utils.base_func.get_amodality_choices, max_length=10, verbose_name='Modality')),
                ('total_count', models.IntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('verified', models.BooleanField(default=False)),
                ('UploadHistory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='minibooks.uploadhistory')),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.company', verbose_name='병원명')),
                ('platform', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='product.platform')),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='의사명')),
            ],
            options={
                'verbose_name': 'reportmasterstat',
                'db_table': 'reportmasterstat',
                'managed': True,
            },
        ),
    ]