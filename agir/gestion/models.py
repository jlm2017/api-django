import dynamic_filenames
from django.db import models

import reversion
from phonenumber_field.modelfields import PhoneNumberField

from agir.gestion.typologies import TypeProjet
from agir.lib.model_fields import IBANField
from agir.lib.models import LocationMixin


@reversion.register()
class Compte(models.Model):
    """Le compte regroupe un ensemble de dépenses

    Il est identifié par son nom et par une désignation courte (max 5 caractères)
    qui permet de le saisir rapidement dans les formulaires.
    """

    designation = models.CharField(
        verbose_name="Désignation courte", max_length=5, blank=False, unique=True
    )
    nom = models.CharField(
        verbose_name="Nom complet du compte", max_length=200, blank=False
    )

    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"


@reversion.register()
class Projet(models.Model):
    """Le projet regroupe ensemble des dépenses liées entre elles

    Un projet peut correspondre à un événement, ou à un type de de dépense précis.
    (par exemple « organisation du meeting du 16 janvier » ou « paiement salaire mars »)
    """

    nom = models.CharField(verbose_name="Nom du projet")
    type = models.CharField(verbose_name="Type de projet", choices=TypeProjet.choices)
    description = models.TextField(verbose_name="Description du projet", null=True)
    event = models.ForeignKey(
        verbose_name="Événement sur la plateforme", null=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


@reversion.register()
class Depense(models.Model):
    """Une dépense correspond à un paiement réalisé en lien avec une facture
    """

    numero = models.AutoField(verbose_name="Numéro unique", editable=False, unique=True)
    titre = models.CharField(
        verbose_name="Titre de la dépense",
        help_text="Une description sommaire de la nature de la dépense",
        blank=False,
        max_length=100,
    )

    commentaires = models.TextField(verbose_name="Commentaires")

    compte = models.ForeignKey(
        to="Compte",
        null=False,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le compte dont fait partie cette dépense.",
    )

    projet = models.ForeignKey(
        to="Projet",
        null=True,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le projet éventuel auquel est rattaché cette dépense.",
    )

    montant = models.DecimalField(
        verbose_name="Montant de la dépense", decimal_places=2, null=False
    )

    paiement = models.BooleanField(
        verbose_name="Dépense payée", null=False, default=False
    )

    fournisseur = models.ForeignKey("Fournisseur", null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"


@reversion.register()
class Document(models.Model):
    class Type(models.TextChoices):
        FACTURE = "FAC", "Facture"
        JUSTIFICATIF = "JUS", "Justificatif de dépense"
        DEVIS = "DEV", "Devis"
        AUTRE = "AUT", "Autre (à détailler dans les commentaires)"

    class Besoin(models.TextChoices):
        NECESSAIRE = "NEC", "Strictement nécessaire"
        PREFERABLE = "PRE", "Préférable"
        IGNORER = "IGN", "Peut être ignoré"

    class Statut(models.TextChoices):
        CORRIGER = "COR", "Document à corriger"
        VERIFIER = "INA", "Document à vérifier"
        CONFIRME = "CON", "Document confirmé"

    titre = models.CharField(
        verbose_name="Titre du document",
        help_text="Ce champ est notamment utilisé pour la recherche de documents",
        max_length=200,
    )

    identifiant = models.CharField(
        verbose_name="Identifiant ou numéro",
        max_length=100,
        help_text="Indiquez ici si ce document a un identifiant ou un numéro (numéro de facture ou de devis, identifiant de transaction, etc.)",
    )

    type = models.CharField(
        verbose_name="Type de document", max_length=3, choices=Type.choices
    )
    statut = models.CharField(
        verbose_name="Statut du document", max_length=3, choices=Statut.choices
    )

    commentaires = models.TextField(verbose_name="Commentaires sur ce document")

    fichier = models.FileField(
        verbose_name="Fichier du document",
        null=True,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/{uuid:.2base32}/{uuid}{ext}"
        ),
    )

    class Meta:
        verbose_name = "Document justificatif"
        verbose_name_plural = "Documents justificatifs"


@reversion.register()
class Fournisseur(LocationMixin, models.Model):
    """Ce modèle permet d'enregistrer des fournisseurs récurrents.

    Un fournisseur peut posséder une adresse, un IBAN pour réaliser des virements,
    et des informations de contact.
    """

    nom = models.CharField(verbose_name="Nom du fournisseur", blank=False)
    commentaires = models.TextField(verbose_name="Commentaires")

    iban = IBANField(verbose_name="IBAN du fournisseur", blank=True)

    contact_phone = PhoneNumberField(verbose_name="Numéro de téléphone", blank=True)
    contact_email = models.EmailField(verbose_name="Adresse email", blank=True)
