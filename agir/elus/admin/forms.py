from data_france.models import CodePostal
from django import forms
from django.db import IntegrityError
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from agir.elus.models import DELEGATIONS_CHOICES
from agir.lib.data import FRANCE_COUNTRY_CODES
from agir.people.actions.subscription import (
    SUBSCRIPTION_TYPE_NSP,
    SUBSCRIPTION_TYPE_ADMIN,
)
from agir.people.models import PersonEmail, Person

PERSON_FIELDS = [
    "last_name",
    "first_name",
    "gender",
    "date_of_birth",
    "is_insoumise",
    "is_2022",
    "contact_phone",
    "location_address1",
    "location_address2",
    "location_zip",
    "location_city",
    "location_country",
    "membre_reseau_elus",
    "commentaires",
]

creer_mandat_declared_fields = {
    f.name: f.formfield() for f in Person._meta.get_fields() if f.name in PERSON_FIELDS
}


class CreerMandatForm(forms.ModelForm):
    email_officiel = forms.ModelChoiceField(
        label="Email officiel", queryset=PersonEmail.objects.none(), required=False
    )
    new_email = forms.EmailField(label="Ajouter un email officiel", required=False)
    delegations = forms.MultipleChoiceField(
        choices=DELEGATIONS_CHOICES,
        label="Délégations (pour un maire adjoint ou un vice-président)",
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    signataire_appel = forms.BooleanField(
        label="Signataire de l'appel des élus", required=False
    )

    def __init__(self, *args, initial=None, instance=None, **kwargs):
        # set up initial values for person fields before calling super constructor
        initial = initial or {}
        if person := instance and getattr(instance, "person", None):
            for f in PERSON_FIELDS:
                initial.setdefault(f, getattr(person, f))
            initial.setdefault(
                "signataire_appel",
                person.meta.get("subscriptions", {}).get("NSP", {}).get("mandat")
                is not None,
            )

        super().__init__(*args, initial=initial, instance=instance, **kwargs)

        if "person" in self.fields:
            self.fields["person"].label = "Compte plateforme de l'élu"
            # on retire les champs de personne
            for name in PERSON_FIELDS:
                del self.fields[name]

        if person is not None:
            for f in PERSON_FIELDS:
                self.fields[f].initial = getattr(person, f)
            self.fields["email_officiel"].queryset = person.emails.all()

        if "email_officiel" not in self._meta.fields:
            del self.fields["email_officiel"]

    def clean(self):
        cleaned_data = super().clean()

        if "person" in self.fields:
            person = cleaned_data.get("person")
        else:
            person = getattr(self.instance, "person", None)

        new_email = cleaned_data.get("new_email")
        contact_phone = cleaned_data.get("contact_phone")
        last_name = cleaned_data.get("last_name")
        first_name = cleaned_data.get("first_name")
        email_officiel = cleaned_data.get("email_officiel")

        minimal_information = (
            person or new_email or contact_phone or (last_name and first_name)
        )

        if not minimal_information:
            self.add_error(
                None,
                "Sélectionnez un compte existant ou indiquez adresse email, numéro de téléphone ou nom/prénom pour"
                " créer une fiche élue sans compte.",
            )

        if new_email and person:
            try:
                person_email = PersonEmail.objects.get_by_natural_key(new_email)
            except PersonEmail.DoesNotExist:
                pass
            else:
                if person_email.person != person:
                    self.add_error(
                        "new_email",
                        "Cette adresse email est déjà utilisée associée à quelqu'un d'autre sur la plateforme.",
                    )

        if new_email and not person:
            try:
                person = Person.objects.get_by_natural_key(new_email)
            except Person.DoesNotExist:
                pass
            else:
                cleaned_data["person"] = person
                del cleaned_data["new_email"]

        if email_officiel and person and email_officiel.person != person:
            cleaned_data["email_officiel"] = None

        if cleaned_data.get("signataire_appel") and not cleaned_data.get(
            "is_2022", person and person.is_2022
        ):
            self.add_error(
                "signataire_appel",
                "Impossible d'indiquer qu'un élu a signé l'appel des élus pour 2022 s'il n'est pas signataire NSP.",
            )

        return cleaned_data

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        if "person" in self.fields:
            person = cleaned_data["person"]
        else:
            person = getattr(self.instance, "person", None)

        if not person:
            # création d'une personne
            now = timezone.now().isoformat()
            meta = {
                "subscriptions": {SUBSCRIPTION_TYPE_ADMIN: {"date": now, "how": "élus"}}
            }
            if self.cleaned_data.get("signataire_appel"):
                meta["subscriptions"][SUBSCRIPTION_TYPE_NSP] = {"mandat": "manuel"}

            self.instance.person = Person.objects.create_person(
                cleaned_data["new_email"],
                **{k: v for k, v in cleaned_data.items() if k in PERSON_FIELDS},
                meta=meta,
            )
            self.instance.email_officiel = self.instance.person.primary_email
        else:
            # On n'assigne les champs de personne QUE dans le cas on on a pas sélectionné une personne
            if "person" not in self.fields:
                if (
                    any(f in self.changed_data for f in PERSON_FIELDS)
                    or "signataire_appel" in self.changed_data
                ):
                    for f in PERSON_FIELDS:
                        setattr(person, f, cleaned_data[f])

                    signataire = cleaned_data["signataire_appel"]
                    deja_signataire = (
                        person.meta.get("subscriptions", {})
                        .get(SUBSCRIPTION_TYPE_NSP, {})
                        .get("mandat")
                        is not None
                    )
                    if signataire and not deja_signataire:
                        person.meta.setdefault("subscriptions", {}).setdefault(
                            SUBSCRIPTION_TYPE_NSP, {}
                        )["mandat"] = "manuel"
                    elif not signataire and deja_signataire:
                        del person.meta["subscriptions"][SUBSCRIPTION_TYPE_NSP][
                            "mandat"
                        ]

                    person.save()

            if "new_email" in self.changed_data:
                try:
                    email = person.add_email(cleaned_data["new_email"])
                except IntegrityError:
                    pass
                else:
                    self.instance.email_officiel = email

        return super().save(commit=commit)


# Inspiré du code de DeclarativeFieldsMetaclass et ModelFormMetaclass
# base_fields et declared_fields semblent toujours etre le meme objet
creer_mandat_declared_fields.update(CreerMandatForm.declared_fields)
CreerMandatForm.base_fields = (
    CreerMandatForm.declared_fields
) = creer_mandat_declared_fields


def legender_depuis_fiche_rne(form, reference):
    form.fields["reference"].help_text = format_html(
        '<a href="{}">{}</a>',
        reverse("admin:data_france_elumunicipal_change", args=(reference.id,)),
        "Voir la fiche dans le Répertoire National des élus",
    )

    form.fields["mandat"].help_text = f"Dans la fiche RNE : {reference.fonction}"

    form.fields["last_name"].help_text = f"Dans la fiche RNE : {reference.nom}"
    form.fields["first_name"].help_text = f"Dans la fiche RNE : {reference.prenom}"
    form.fields[
        "date_of_birth"
    ].help_text = f"Dans la fiche RNE : {reference.date_naissance.strftime('%d/%m/%Y')}"
    form.fields[
        "gender"
    ].help_text = f"Sexe à l'état civil dans la fiche RNE : {reference.sexe}"
    form.fields[
        "dates"
    ].help_text = (
        f"Dates de début du mandat dans la fiche RNE : {reference.date_debut_mandat}"
    )

    if (
        form.initial["location_zip"]
        and form.initial["location_country"] in FRANCE_COUNTRY_CODES
    ):
        try:
            code_postal = CodePostal.objects.get(code=form.initial["location_zip"])
        except CodePostal.DoesNotExist:
            form.fields["location_zip"].help_text = "Ce code postal est inconnu"
        else:
            form.fields["location_zip"].help_text = format_html(
                '<a href="{}">{}</a>',
                reverse("admin:data_france_codepostal_change", args=(code_postal.id,)),
                "Voir la fiche pour ce code postal",
            )


class CreerMandatMunicipalForm(CreerMandatForm):
    def __init__(self, *args, instance=None, **kwargs):
        super().__init__(*args, instance=instance, **kwargs)

        if "communautaire" in self.fields:
            if self.instance.conseil is None or self.instance.conseil.epci is None:
                self.fields["communautaire"].disabled = True
            else:
                epci = self.instance.conseil.epci
                self.fields["communautaire"].label = f"Mandat auprès de la {epci.nom}"

        if instance and instance.reference:
            legender_depuis_fiche_rne(self, instance.reference)
