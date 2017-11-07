# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-07 14:51
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0017_help_text_on_location_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonForm',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, verbose_name='Titre')),
                ('slug', models.SlugField(verbose_name='Slug')),
                ('published', models.BooleanField(default=True, verbose_name='Publié')),
                ('description', models.TextField(help_text='Description visible sur la page au remplissage du formulaire', verbose_name='Description')),
                ('confirmation_note', models.TextField(help_text="Note montrée à l'utilisateur une fois le formulaire validé.", verbose_name='Note après complétion')),
                ('main_question', models.CharField(max_length=200, verbose_name='Intitulé de la question principale')),
                ('personal_information', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=150), blank=True, default=list, help_text='Une liste de champs de personnes à demander aux personnes qui remplissent le formulaire.', size=None, verbose_name='Informations personnelles requises')),
                ('additional_fields', django.contrib.postgres.fields.jsonb.JSONField(default=list, verbose_name='Champs additionnels', blank=True)),
                ('tags', models.ManyToManyField(related_name='forms', related_query_name='form', to='people.PersonTag')),
            ],
            options={
                'verbose_name': 'Formulaire',
            },
        ),
        migrations.CreateModel(
            name='PersonFormSubmission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(editable=False, verbose_name='Données')),
                ('form', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='submissions', to='people.PersonForm')),
                ('person', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='form_submissions', to='people.Person')),
            ],
        ),
        migrations.AlterModelOptions(
            name='personemail',
            options={'verbose_name': 'Email'},
        ),
    ]
