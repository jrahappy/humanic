# Generated by Django 5.1 on 2024-12-29 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0024_alter_company_is_collab'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='is_tele',
            field=models.BooleanField(blank=True, default=False, null=True),
        ),
    ]
