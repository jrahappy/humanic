# Generated by Django 5.1 on 2024-12-19 22:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0009_alter_refers_referred_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReferSimpleDiagnosis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('diagnosis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collab.simplediagnosis')),
                ('refer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collab.refers')),
            ],
        ),
    ]
