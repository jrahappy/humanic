# Generated by Django 5.1 on 2024-11-21 14:45

import taggit.managers
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('customer', '0021_company_tags'),
        ('taggit', '0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
    ]