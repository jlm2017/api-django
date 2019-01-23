# Generated by Django 2.0.6 on 2018-07-19 14:55
import agir.lib.form_fields
import agir.people.models
import agir.people.person_forms.models
import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("people", "0034_personform_send_answers_to")]

    operations = [
        migrations.AlterField(
            model_name="personformsubmission",
            name="data",
            field=django.contrib.postgres.fields.jsonb.JSONField(
                editable=False,
                encoder=agir.lib.form_fields.CustomJSONEncoder,
                verbose_name="Données",
            ),
        )
    ]
