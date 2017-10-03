# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-02 15:00
from __future__ import unicode_literals

from django.db import migrations
from django.utils.text import slugify


def populate_calendar_titles(apps, schema):
    Calendar = apps.get_model('events', 'Calendar')

    for calendar in Calendar.objects.all():
        calendar.name = calendar.description[:255] if calendar.description else calendar.label
        calendar.slug = slugify(calendar.label)[:50]
        calendar.save()


def unpopulate_calendar_titles(apps, schema):
    Calendar = apps.get_model('events', 'Calendar')

    Calendar.objects.update(title='', slug='')


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_calendar_new_fields'),
    ]

    operations = [
        migrations.RunPython(populate_calendar_titles, unpopulate_calendar_titles)
    ]
