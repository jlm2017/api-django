from functools import partial

import dateutil
from django import forms
from django.contrib import admin
from django.contrib.admin.options import BaseModelAdmin
from django.utils import timezone
from django.utils.html import format_html_join
from reversion.admin import VersionAdmin

from agir.gestion.models import Depense, Projet, Compte, Document, Fournisseur
from agir.people.models import Person


class CommentairesForm(forms.ModelForm):
    nouveau_commentaire = forms.CharField(
        label="Ajouter un commentaire", required=False, widget=forms.Textarea()
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.cleaned_data.get("nouveau_commentaire"):
            self.instance.commentaires.append(
                {
                    "auteur": str(self.user.person.id),
                    "date": timezone.now().isoformat(),
                    "message": self.cleaned_data["nouveau_commentaire"],
                }
            )
        return super().save(commit=commit)


class BaseMixin(BaseModelAdmin):
    form = CommentairesForm

    search_fields = ("numero",)

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            return queryset.search(search_term)
        return queryset, False

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj=obj, change=change, **kwargs)
        return partial(form, user=request.user)

    def get_readonly_fields(self, request, obj=None):
        return super().get_readonly_fields(request, obj=obj) + (
            "bloc_commentaires",
            "numero_",
        )

    def numero_(self, obj):
        if obj.id:
            return obj.numero
        else:
            return "-"

    numero_.short_description = "Numéro automatique"

    def bloc_commentaires(self, obj):
        if obj and obj.commentaires:
            return format_html_join(
                "",
                "<div><strong>{} — {}</strong><p>{}</p></div>",
                (
                    (
                        Person.objects.filter(id=com["auteur"]).first(),
                        dateutil.parser.parse(com["date"]).strftime(
                            "%H:%M le %d/%m/%Y"
                        ),
                        com["message"],
                    )
                    for com in obj.commentaires
                ),
            )

        return "Aucun commentaire."

    bloc_commentaires.short_description = "Commentaires"


@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ("designation", "nom", "description")
    fields = ("designation", "nom", "description")


@admin.register(Fournisseur)
class FournisseurAdmin(VersionAdmin):
    list_display = ("nom", "contact_phone", "contact_email")

    fieldsets = (
        (None, {"fields": ("nom", "contact_phone", "contact_email")}),
        ("Paiement", {"fields": ("iban",)}),
        (
            "Adresse de facturation",
            {
                "fields": (
                    "location_address1",
                    "location_address2",
                    "location_zip",
                    "location_city",
                    "location_country",
                )
            },
        ),
    )


@admin.register(Document)
class DocumentAdmin(BaseMixin, VersionAdmin):
    list_display = (
        "numero",
        "titre",
        "identifiant",
        "type",
        "statut",
        "requis",
    )

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "numero_",
                    "titre",
                    "identifiant",
                    "type",
                    "statut",
                    "requis",
                    "fichier",
                )
            },
        ),
        ("Commentaires", {"fields": ("bloc_commentaires", "nouveau_commentaire")}),
    )


class DocumentInlineForm(forms.ModelForm):
    DOCUMENTS_FIELDS = ("titre", "type", "statut", "fichier")

    def __init__(self, *args, initial=None, instance=None, **kwargs):
        if initial is None:
            initial = {}

        if instance and instance.document:
            for f in self.DOCUMENTS_FIELDS:
                initial.setdefault(f, getattr(instance.document, f))

        super().__init__(*args, instance=instance, initial=initial, **kwargs)

        if instance and instance.document:
            self.fields["document"].disabled = True
        else:
            for f in self.DOCUMENTS_FIELDS:
                self.fields[f].disabled = True


_document_fields = {
    f.name: f.formfield()
    for f in Document._meta.get_fields()
    if f.name in DocumentInlineForm.DOCUMENTS_FIELDS
}
_document_fields.update(DocumentInlineForm.declared_fields)
DocumentInlineForm.base_fields = DocumentInlineForm.declared_fields = _document_fields


class BaseDocumentInline(admin.TabularInline):
    extra = 0
    show_change_link = True
    form = DocumentInlineForm

    autocomplete_fields = ("document",)

    fields = ("document", *DocumentInlineForm.DOCUMENTS_FIELDS)


class DepenseDocumentInline(BaseDocumentInline):
    model = Depense.documents.through


@admin.register(Depense)
class DepenseAdmin(BaseMixin, VersionAdmin):
    list_display = (
        "numero_",
        "titre",
        "montant",
        "paiement",
        "compte",
        "projet",
    )

    fieldsets = (
        (None, {"fields": ("numero_", "titre", "compte", "montant", "description",)},),
        ("Informations de paiement", {"fields": ("fournisseur", "paiement")}),
        ("Commentaires", {"fields": ("bloc_commentaires", "nouveau_commentaire")}),
    )

    inlines = [DepenseDocumentInline]


class DepenseInline(BaseMixin, admin.TabularInline):
    model = Depense
    extra = 0
    show_change_link = True

    fields = ("numero_", "titre", "montant", "paiement", "compte")


class ProjetDocumentInline(BaseDocumentInline):
    model = Projet.documents.through


@admin.register(Projet)
class ProjetAdmin(BaseMixin, VersionAdmin):
    list_display = ("numero", "titre", "type", "statut")

    fieldsets = (
        (
            None,
            {"fields": ("numero", "titre", "type", "statut", "event", "description")},
        ),
        ("Commentaires", {"fields": ("bloc_commentaires", "nouveau_commentaire")}),
    )

    readonly_fields = ("numero",)

    inlines = [DepenseInline, ProjetDocumentInline]
