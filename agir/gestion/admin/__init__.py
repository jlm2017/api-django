from functools import partial

from django import forms
from django.contrib import admin
from django.utils.html import format_html_join

from agir.gestion.models import Depense, Projet, Compte, Document, Fournisseur


class CommentairesForm(forms.ModelForm):
    nouveau_commentaire = forms.CharField(
        label="Ajouter un commentaire", required=False, widget=forms.Textarea()
    )

    def __init__(self, *args, user, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        if self.cleaned_data.get("nouveau_commentaire"):
            self.instance.commentaires.append(
                {
                    "auteur": None,
                    "date": None,
                    "message": self.cleaned_data["nouveau_commentaire"],
                }
            )
        return super().save(commit=commit)


class BaseMixin(admin.ModelAdmin):
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
        return super().get_readonly_fields(request, obj=obj) + ("bloc_commentaires",)

    def bloc_commentaires(self, obj):
        if obj and obj.commentaires:
            return format_html_join(
                "",
                "<div><strong>{} — {}</strong><p>{}</p></div>",
                (
                    (com["auteur"], com["date"], com["message"])
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
class FournisseurAdmin(admin.ModelAdmin):
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
class DocumentAdmin(BaseMixin, admin.ModelAdmin):
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
                    "numero",
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

    readonly_fields = ("numero",)


class BaseDocumentInline(admin.TabularInline):
    extra = 0
    show_change_link = True

    autocomplete_fields = ("document",)

    # fields = readonly_fields = (
    #     "numero",
    #     "titre",
    #     "type",
    #     "statut",
    #     "requis",
    #     "fichier",
    # )


class DepenseDocumentInline(BaseDocumentInline):
    model = Depense.documents.through


@admin.register(Depense)
class DepenseAdmin(BaseMixin, admin.ModelAdmin):
    list_display = (
        "numero",
        "titre",
        "montant",
        "paiement",
        "compte",
        "projet",
    )

    readonly_fields = ("numero",)

    fieldsets = (
        (None, {"fields": ("numero", "titre", "compte", "montant", "description")}),
        ("Informations de paiement", {"fields": ("fournisseur", "paiement")}),
        ("Commentaires", {"fields": ("bloc_commentaires", "nouveau_commentaire")}),
    )

    inlines = [DepenseDocumentInline]


class DepenseInline(admin.StackedInline):
    model = Depense
    extra = 0
    show_change_link = True

    fields = (
        "numero",
        "titre",
        "montant",
        "paiement",
        "compte",
    )
    readonly_fields = ("numero",)


class ProjetDocumentInline(BaseDocumentInline):
    model = Projet.documents.through


@admin.register(Projet)
class ProjetAdmin(BaseMixin, admin.ModelAdmin):
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
