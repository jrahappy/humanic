# Generated by Django 5.1 on 2024-09-21 03:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0018_humanrules_rules_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmaster',
            name='pay_to_human',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
        migrations.AddField(
            model_name='reportmaster',
            name='pay_to_service',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]