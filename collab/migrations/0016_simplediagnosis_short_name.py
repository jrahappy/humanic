# Generated by Django 5.1 on 2024-12-27 19:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collab', '0015_myillnesscode_mysimplediagnosis'),
    ]

    operations = [
        migrations.AddField(
            model_name='simplediagnosis',
            name='short_name',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]