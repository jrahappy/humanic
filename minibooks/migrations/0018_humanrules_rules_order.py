# Generated by Django 5.1 on 2024-09-20 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0017_magamdetail_affected_rows_magammaster_target_rows'),
    ]

    operations = [
        migrations.AddField(
            model_name='humanrules',
            name='rules_order',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
