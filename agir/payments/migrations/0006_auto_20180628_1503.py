# Generated by Django 2.0.6 on 2018-06-28 13:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0005_auto_20180615_1804'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='payment',
            options={'get_latest_by': 'created'},
        ),
    ]
