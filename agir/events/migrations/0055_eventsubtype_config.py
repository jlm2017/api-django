# Generated by Django 2.0.9 on 2018-10-23 16:19

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0054_auto_20181009_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventsubtype',
            name='config',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict, verbose_name='Configuration'),
        ),
    ]