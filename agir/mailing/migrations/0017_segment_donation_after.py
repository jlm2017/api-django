# Generated by Django 2.2.8 on 2019-12-13 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("mailing", "0016_segment_subscription")]

    operations = [
        migrations.AddField(
            model_name="segment",
            name="donation_after",
            field=models.DateField(
                blank=True,
                help_text="Écrivez en toute lettre JJ/MM/AAAA plutôt qu'avec le widget, ça ira plus vite.",
                null=True,
                verbose_name="A fait au moins un don (hors don mensuel) depuis le",
            ),
        )
    ]
