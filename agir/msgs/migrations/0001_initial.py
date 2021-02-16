# Generated by Django 3.1.6 on 2021-02-05 10:38

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import stdimage.models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("people", "0003_segments"),
        ("contenttypes", "0002_remove_content_type_name"),
        ("groups", "0002_creer_sous_types"),
        ("events", "0002_objets_initiaux_et_recherche"),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportGroupMessage",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="UUID interne à l'API pour identifier la ressource",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                ("text", models.TextField(max_length=2000, verbose_name="Contenu")),
                ("image", stdimage.models.StdImageField(upload_to="")),
                ("deleted", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="people.person",
                        verbose_name="Auteur",
                    ),
                ),
                (
                    "linked_event",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="events.event",
                        verbose_name="Événement lié",
                    ),
                ),
                (
                    "supportgroup",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="messages",
                        to="groups.supportgroup",
                        verbose_name="Groupe / équipe",
                    ),
                ),
            ],
            options={
                "verbose_name": "Message de groupe",
                "verbose_name_plural": "Messages de groupe",
            },
        ),
        migrations.CreateModel(
            name="UserReport",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                ("object_id", models.UUIDField()),
                (
                    "content_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="contenttypes.contenttype",
                        verbose_name="Type",
                    ),
                ),
                (
                    "reporter",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="people.person",
                        verbose_name="Personne à l'origine du signalement",
                    ),
                ),
            ],
            options={
                "abstract": False,
                "verbose_name": "Signalement",
                "verbose_name_plural": "Signalements",
            },
        ),
        migrations.CreateModel(
            name="SupportGroupMessageComment",
            fields=[
                (
                    "created",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        help_text="UUID interne à l'API pour identifier la ressource",
                        primary_key=True,
                        serialize=False,
                        verbose_name="UUID",
                    ),
                ),
                ("text", models.TextField(max_length=2000, verbose_name="Contenu")),
                ("image", stdimage.models.StdImageField(upload_to="")),
                ("deleted", models.BooleanField(default=False)),
                (
                    "author",
                    models.ForeignKey(
                        editable=False,
                        on_delete=django.db.models.deletion.PROTECT,
                        to="people.person",
                        verbose_name="Auteur",
                    ),
                ),
                (
                    "message",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="comments",
                        to="msgs.supportgroupmessage",
                        verbose_name="Message initial",
                    ),
                ),
            ],
            options={
                "verbose_name": "Commentaire de messages de groupe",
                "verbose_name_plural": "Commentaires de messages de groupe",
            },
        ),
    ]