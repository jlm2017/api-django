import re
import secrets
from functools import reduce
from string import ascii_uppercase, digits
from operator import add

import dynamic_filenames
from django.contrib.postgres.search import SearchVector, SearchRank
from django.db import models

import reversion
from phonenumber_field.modelfields import PhoneNumberField

from agir.gestion.typologies import TypeProjet, TypeDocument, Etat
from agir.lib.model_fields import IBANField
from agir.lib.models import LocationMixin
from agir.lib.search import PrefixSearchQuery

ALPHABET = ascii_uppercase + digits

NUMERO_RE = re.compile("^[A-Z0-9]{3}-[A-Z0-9]{1,3}$")


def numero_unique():
    chars = [secrets.choice(ALPHABET) for _ in range(6)]
    return f"{''.join(chars[:3])}-{''.join(chars[3:])}"


class NumeroQueryset(models.QuerySet):
    def search(self, query):

        if NUMERO_RE.match(query):
            return self.filter(numero__startswith=query)

        search_config = self.model.search_config
        vector = reduce(
            add,
            (
                SearchVector(models.F(field), config=config, weight=weight)
                for field, config, weight in search_config
            ),
        )

        query = PrefixSearchQuery(
            query, config="french_unaccented"
        ) | PrefixSearchQuery(query, config="simple_unaccented")

        return (
            self.annotate(search=vector)
            .filter(search=query)
            .annotate(rank=SearchRank(vector, query))
            .order_by("-rank")
        )


class NumeroManager(models.Manager):
    def get_queryset(self):
        return NumeroQueryset(self.model, using=self._db)

    def get_by_natural_key(self, numero):
        return self.get(numero=numero)


class NumeroUniqueMixin(models.Model):
    objects = NumeroManager()

    numero = models.CharField(
        verbose_name="Numéro unique",
        max_length=7,
        editable=False,
        blank=False,
        default=numero_unique,
        unique=True,
        help_text="Numéro unique pour identifier chaque objet sur la plateforme.",
    )

    commentaires = models.JSONField(
        verbose_name="Commentaires",
        default=list,
        help_text="Ces commentaires permettent d'ajouter de garder la trace des opérations de traitement des différentes pièces.",
    )

    def __str__(self):
        titre = f"{self.titre[70:]}..." if len(self.titre) > 70 else self.titre
        return f"« {titre} » ({self.numero})"

    class Meta:
        abstract = True


@reversion.register()
class Document(NumeroUniqueMixin, models.Model):
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
        help_text="Titre permettant d'identifier le document",
        max_length=200,
    )

    identifiant = models.CharField(
        verbose_name="Identifiant ou numéro externe",
        max_length=100,
        blank=True,
        help_text="Indiquez ici si ce document a un identifiant ou un numéro (numéro de facture ou de devis, identifiant de transaction, etc.)",
    )

    type = models.CharField(
        verbose_name="Type de document", max_length=10, choices=TypeDocument.choices
    )
    statut = models.CharField(
        verbose_name="Statut du document", max_length=3, choices=Statut.choices
    )

    requis = models.CharField(
        verbose_name="Obligatoire ?", max_length=3, choices=Besoin.choices
    )

    description = models.TextField(
        "Description du document",
        help_text="Toute description complémentaire nécessaire pour identifier clairement le document (et le rechercher)",
        blank=True,
    )

    fichier = models.FileField(
        verbose_name="Fichier du document",
        null=True,
        blank=True,
        upload_to=dynamic_filenames.FilePattern(
            filename_pattern="gestion/documents/{uuid:.2base32}/{uuid}{ext}"
        ),
    )

    search_config = (
        ("numero", "simple_unaccented", "B"),
        ("titre", "french_unaccented", "A"),
        ("identifiant", "simple_unaccented", "B"),
        ("description", "french_unaccented", "C"),
    )

    class Meta:
        verbose_name = "Document justificatif"
        verbose_name_plural = "Documents justificatifs"


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
    description = models.TextField(verbose_name="Description", blank=True)

    def __str__(self):
        return f"{self.nom} ({self.designation})"

    class Meta:
        verbose_name = "Compte"
        verbose_name_plural = "Comptes"


@reversion.register()
class Projet(NumeroUniqueMixin, models.Model):
    """Le projet regroupe ensemble des dépenses liées entre elles

    Un projet peut correspondre à un événement, ou à un type de de dépense précis.
    (par exemple « organisation du meeting du 16 janvier » ou « paiement salaire mars »)
    """

    class StatutProjet(models.TextChoices):
        DEMANDE_FINANCEMENT = "DFI", "Demande de financement"
        EN_CONSTITUTION = "ECO", "En cours de constitution"
        FINALISE = "FIN", "Finalisé par le secrétariat"
        RENVOI = "REN", "Renvoyé par l'équipe financière"

    titre = models.CharField(verbose_name="Titre du projet", max_length=40)
    type = models.CharField(
        verbose_name="Type de projet", choices=TypeProjet.choices, max_length=10
    )
    statut = models.CharField(
        verbose_name="Statut", max_length=3, choices=StatutProjet.choices, blank=False
    )
    description = models.TextField(verbose_name="Description du projet", null=True)
    event = models.ForeignKey(
        to="events.Event",
        verbose_name="Événement sur la plateforme",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    details = models.JSONField("Détails", default=dict)

    documents = models.ManyToManyField(
        to="Document", related_name="projets", related_query_name="projet"
    )

    class Meta:
        verbose_name = "Projet"
        verbose_name_plural = "Projets"


@reversion.register()
class Depense(NumeroUniqueMixin, models.Model):
    """Une dépense correspond à un paiement réalisé en lien avec une facture
    """

    titre = models.CharField(
        verbose_name="Titre de la dépense",
        help_text="Une description sommaire de la nature de la dépense",
        blank=False,
        max_length=100,
    )

    description = models.TextField(
        verbose_name="Description",
        help_text="La description doit permettre de pouvoir identifier de façon non ambigue la dépense et sa nature dans le cas où le titre ne suffit pas.",
        blank=True,
    )

    compte = models.ForeignKey(
        to="Compte",
        null=False,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le compte dont fait partie cette dépense.",
        on_delete=models.PROTECT,
    )

    projet = models.ForeignKey(
        to="Projet",
        null=True,
        related_name="depenses",
        related_query_name="depense",
        help_text="Le projet éventuel auquel est rattaché cette dépense.",
        on_delete=models.SET_NULL,
    )

    montant = models.DecimalField(
        verbose_name="Montant de la dépense",
        decimal_places=2,
        null=False,
        max_digits=10,
    )

    paiement = models.BooleanField(
        verbose_name="Dépense payée", null=False, default=False
    )

    documents = models.ManyToManyField(
        to="Document", related_name="depenses", related_query_name="depense",
    )

    fournisseur = models.ForeignKey("Fournisseur", null=True, on_delete=models.SET_NULL)

    # informations fournisseurs
    nom_fournisseur = models.CharField(
        verbose_name="Nom du fournisseur", blank=False, max_length=100
    )

    iban_fournisseur = IBANField(verbose_name="IBAN du fournisseur", blank=True)

    contact_phone_fournisseur = PhoneNumberField(
        verbose_name="Numéro de téléphone", blank=True
    )
    contact_email_fournisseur = models.EmailField(
        verbose_name="Adresse email", blank=True
    )

    @property
    def facture_presente(self):
        return self.documents.filter(
            type=TypeDocument.FACTURE, statut=Document.Statut.CONFIRME
        ).exists

    @property
    def paiement_effectue(self):
        return self.documents.filter(
            type=TypeDocument.PAIEMENT, statut=Document.Statut.CONFIRME
        ).exists()

    @property
    def etat(self):
        if not self.facture_presente or not self.paiement_effectue:
            return Etat.UNFINISHED
        if (
            self.documents.filter(requis=Document.Besoin.NECESSAIRE)
            .exclude(statut=Document.Statut.CONFIRME)
            .exists()
        ):
            return Etat.UNFINISHED
        if (
            self.documents.filter(requis=Document.Besoin.PREFERABLE)
            .exclude(statut=Document.Statut.CONFIRME)
            .exists()
        ):
            return Etat.WARNING
        return Etat.OK

    class Meta:
        verbose_name = "Dépense"
        verbose_name_plural = "Dépenses"


@reversion.register()
class Fournisseur(LocationMixin, models.Model):
    """Ce modèle permet d'enregistrer des fournisseurs récurrents.

    Un fournisseur peut posséder une adresse, un IBAN pour réaliser des virements,
    et des informations de contact.
    """

    nom = models.CharField(
        verbose_name="Nom du fournisseur", blank=False, max_length=100
    )
    commentaires = models.TextField(verbose_name="Commentaires")

    iban = IBANField(verbose_name="IBAN du fournisseur", blank=True)

    contact_phone = PhoneNumberField(verbose_name="Numéro de téléphone", blank=True)
    contact_email = models.EmailField(verbose_name="Adresse email", blank=True)

    def __str__(self):
        return self.nom
