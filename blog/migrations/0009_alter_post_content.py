# Generated by Django 5.1 on 2024-10-22 13:04

# import django_ckeditor_5.fields
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    dependencies = [
        ("blog", "0008_alter_postattachment_file"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="content",
            # field=django_ckeditor_5.fields.CKEditor5Field(default=False, verbose_name='Text'),
            field=models.TextField(),
            preserve_default=False,
        ),
    ]
