# Generated by Django 2.0.5 on 2018-06-05 16:04

import agir.lib.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0032_auto_20180426_1716'),
    ]

    operations = [
        migrations.AddField(
            model_name='personform',
            name='send_confirmation',
            field=models.BooleanField(default=False, verbose_name='Envoyer une confirmation par email'),
        ),
        migrations.AlterField(
            model_name='personform',
            name='confirmation_note',
            field=agir.lib.models.DescriptionField(help_text="Note montrée (et éventuellement envoyée par email) à l'utilisateur une fois le formulaire validé.", verbose_name='Note après complétion'),
        ),
    ]