from django.db.models import TextChoices


class Etat(TextChoices):
    OK = "OK", "Dossier complet"
    WARNING = "WARN", "Problèmes potentiels"
    UNFINISHED = "ERR", "Éléments manquants"


class TypeDocument(TextChoices):
    FACTURE = "FAC", "Facture"
    JUSTIFICATIF = "JUS", "Justificatif de dépense"
    DEVIS = "DEV", "Devis"
    PAIEMENT = "PAY", "Preuve de paiement"
    ATTESTATION_GRATUITE = "GRA", "Attestation de gratuité"
    AUTRE = "AUT", "Autre (à détailler dans les commentaires)"


class TypeDepense(TextChoices):
    FOURNITURE_MARCHANDISES = "AFM", "Achats de fournitures et marchandises"
    FOURNITURE_BUREAU = "AFM-B", "Achats de fourniture de bureau"
    FOURNITURE_GOODIES = "AFM-G", "Achats de goodies"

    FRAIS_BANCAIRES = "FBC", "Frais bancaires"

    FRAIS_DIVERS = "FDV", "Frais divers"

    FRAIS_RECEPTION_HEBERGEMENT = "FRH", "Frais de réception et d'hébergement"
    FRAIS_HEBERGEMENT = "FRH-H", "Frais d'hébergement"
    FRAIS_ALIMENTATION = "FRH-A", "Frais de restauration"

    HONORAIRES_EXPERT_COMPTABLE = "HEC", "Honoraires de l'expert comptable"

    HONORAIRES_CONSEILS_COMMUNICATION = "HCC", "Honoraires et conseils en communication"
    GRAPHISME_MAQUETTAGE = "HCC-G", "Graphisme et maquettage"
    CONSEIL_COMMUNICATION = "HCC-C", "Conseil en communication"

    FRAIS_IMMOBILIERS = "IMM", "Location ou mise à disposition immobilière"
    LOCATION_SALLE_EVENEMENT = "IMM-S", "Mise à disposition d'une salle"
    LOYERS = "IMM-L", "Loyers de location"

    PRODUCTION_AUDIOVISUELLE = "PAU", "Production audiovisuelle"

    PUBLICATION_IMPRESSION = "PIM", "Publication et impression (hors R39)"

    REUNIONS_PUBLIQUES = "Frais divers liées aux réunions publiques"

    TRANSPORTS = "TRA", "Transports et déplacement"
    TRAIN = (
        "TRA-T",
        "Billets de train",
    )
    AVION = "TRA-A", "Billets d'avion"
    LOCATION_VEHICULE = "TRA-L", "Location d'un véhicule"
    FRAIS_KILOMETRIQUES = "TRA-K", "Frais kilométriques"


class TypeProjet(TextChoices):
    REUNION_PUBLIQUE = "REU", "Réunion publique"

    MANIFESTATION = "MAN", "Manifestation publique"

    DEPENSES_RH = "RH", "Dépenses RH mensuelles"
