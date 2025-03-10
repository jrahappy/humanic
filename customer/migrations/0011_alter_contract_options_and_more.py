# Generated by Django 5.1 on 2024-10-01 17:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0010_contract_contract_type'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contract',
            options={},
        ),
        migrations.RemoveField(
            model_name='contract',
            name='contract_description',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='contract_end',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='contract_name',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='contract_start',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='contract_type',
        ),
        migrations.AddField(
            model_name='company',
            name='is_clinic',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='contract',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='ServiceFee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('category', models.CharField(choices=[('P', 'Percent'), ('F', 'Flat Fee')], default='P', max_length=1)),
                ('rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.company')),
            ],
        ),
    ]
