# Generated by Django 5.1 on 2024-09-20 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0016_humanrules_reportmaster_is_locked_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='magamdetail',
            name='affected_rows',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='magammaster',
            name='target_rows',
            field=models.IntegerField(default=0),
        ),
    ]