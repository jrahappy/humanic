# Generated by Django 5.1 on 2024-09-16 22:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('minibooks', '0011_alter_reportmaster_exelrownum'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reportmaster',
            old_name='exelrownum',
            new_name='excelrownum',
        ),
    ]
