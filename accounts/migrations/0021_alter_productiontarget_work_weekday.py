# Generated by Django 5.1 on 2024-11-16 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_alter_productiontarget_work_weekday_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productiontarget',
            name='work_weekday',
            field=models.CharField(choices=[('0', 'Sunday'), ('1', 'Monday'), ('2', 'Tuesday'), ('3', 'Wednesday'), ('4', 'Thursday'), ('5', 'Friday'), ('6', 'Saturday')], default='1', max_length=1),
        ),
    ]
