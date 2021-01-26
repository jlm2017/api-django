from django.db.models import TextChoices


class TypeProjet(TextChoices):
    REUNION_PUBLIQUE = "RP", "Réunion publique"
    MANIFESTATION = "MA", "Manifestation ou marche"


class TypeDepense(TextChoices):
    FOURNITURE_MARCHANDISES = "AFM"
    FOURNITURE_BUREAU = "AFM-B"
    FOURNITURE_GOODIES = "AFM-G"
