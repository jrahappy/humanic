# Generated by Django 5.1 on 2024-09-25 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0019_reportmaster_pay_to_human_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportmasterstat',
            name='total_revunue',
            field=models.FloatField(blank=True, default=0, null=True),
        ),
    ]
