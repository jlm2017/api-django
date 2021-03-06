from django.urls import path

from . import views


urlpatterns = [
    path("dons/", views.AskAmountView.as_view(), name="donation_amount"),
    path(
        "dons/informations/",
        views.DonationPersonalInformationView.as_view(),
        name="donation_information",
    ),
    path(
        "dons-mensuels/informations/",
        views.MonthlyDonationPersonalInformationView.as_view(),
        name="monthly_donation_information",
    ),
    path(
        "dons-mensuels/deja-donateur/",
        views.AlreadyHasSubscriptionView.as_view(),
        name="already_has_subscription",
    ),
    path(
        "dons-mensuels/confirmer/attente/",
        views.MonthlyDonationEmailSentView.as_view(),
        name="monthly_donation_confirmation_email_sent",
    ),
    path(
        "dons-mensuels/confirmer/",
        views.MonthlyDonationEmailConfirmationView.as_view(),
        name="monthly_donation_confirm",
    ),
    path(
        "groupes/<uuid:group_id>/depenses/",
        views.CreateSpendingRequestView.as_view(),
        name="create_spending_request",
    ),
    path(
        "financement/requete/<uuid:pk>/",
        views.ManageSpendingRequestView.as_view(),
        name="manage_spending_request",
    ),
    path(
        "financement/requete/<uuid:pk>/modifier/",
        views.EditSpendingRequestView.as_view(),
        name="edit_spending_request",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/creer/",
        views.CreateDocumentView.as_view(),
        name="create_document",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/<int:pk>/",
        views.EditDocumentView.as_view(),
        name="edit_document",
    ),
    path(
        "financement/requete/<uuid:spending_request_id>/document/<int:pk>/supprimer/",
        views.DeleteDocumentView.as_view(),
        name="delete_document",
    ),
]
