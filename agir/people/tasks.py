from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from agir.activity.models import Activity
from agir.authentication.tokens import (
    subscription_confirmation_token_generator,
    add_email_confirmation_token_generator,
    merge_account_token_generator,
)
from agir.lib.celery import emailing_task
from agir.lib.display import pretty_time_since
from agir.lib.mailing import send_mosaico_email
from agir.lib.sms import send_sms
from agir.lib.utils import front_url
from .actions.subscription import (
    SUBSCRIPTIONS_EMAILS,
    SUBSCRIPTION_TYPE_LFI,
    SUBSCRIPTION_TYPE_NSP,
)
from .models import Person, PersonFormSubmission, PersonEmail, PersonValidationSMS
from .person_forms.display import default_person_form_display


@emailing_task
def send_welcome_mail(person_pk, type):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)
    message_info = SUBSCRIPTIONS_EMAILS[type].get("welcome")

    if message_info:
        send_mosaico_email(
            code=message_info.code,
            subject=message_info.subject,
            from_email=message_info.from_email,
            bindings={"PROFILE_LINK": front_url("personal_information")},
            recipients=[person],
        )


@emailing_task
def send_confirmation_email(email, type=SUBSCRIPTION_TYPE_LFI, **kwargs):
    if PersonEmail.objects.filter(address__iexact=email).exists():
        p = Person.objects.get_by_natural_key(email)

        if "already_subscribed" in SUBSCRIPTIONS_EMAILS[type]:
            message_info = SUBSCRIPTIONS_EMAILS[type]["already_subscribed"]

            send_mosaico_email(
                code=message_info.code,
                subject=message_info.subject,
                from_email=message_info.from_email,
                bindings={
                    "PANEL_LINK": front_url("dashboard", auto_login=True),
                    "AGO": pretty_time_since(p.created),
                },
                recipients=[p],
            )

        return

    subscription_token = subscription_confirmation_token_generator.make_token(
        email=email, type=type, **kwargs
    )
    confirm_subscription_url = front_url(
        "subscription_confirm", auto_login=False, nsp=type == SUBSCRIPTION_TYPE_NSP
    )
    query_args = {"email": email, "type": type, **kwargs, "token": subscription_token}
    confirm_subscription_url += "?" + urlencode(query_args)

    message_info = SUBSCRIPTIONS_EMAILS[type]["confirmation"]

    send_mosaico_email(
        code=message_info.code,
        subject=message_info.subject,
        from_email=message_info.from_email,
        recipients=[email],
        bindings={"CONFIRMATION_URL": confirm_subscription_url},
    )


@emailing_task
def send_confirmation_merge_account(user_pk_requester, user_pk_merge, **kwargs):
    """Envoie une demande de fusion de compte.

    La premiere clé primaire de person est celle du profil qui va rester, la deuxième est celle du profil qui
    sera supprimé une fois les données du compte fusionnées.

    Si l'un des deux utilisateurs n'existe pas ou que l'utilisateur est le même, l'opération est annulée.
    """
    try:
        requester_email = Person.objects.get(pk=user_pk_requester).email
        merge_email = Person.objects.get(pk=user_pk_merge).email
    except Person.DoesNotExist:
        return

    if user_pk_requester == user_pk_merge:
        return

    subscription_token = merge_account_token_generator.make_token(
        pk_requester=str(user_pk_requester), pk_merge=str(user_pk_merge)
    )
    query_args = {
        "pk_requester": user_pk_requester,
        "pk_merge": user_pk_merge,
        "token": subscription_token,
        **kwargs,
    }
    confirm_merge_account = front_url(
        "confirm_merge_account", query=query_args, auto_login=False
    )

    send_mosaico_email(
        code="MERGE_ACCOUNT_CONFIRMATION",
        subject="Veuillez confirmer la fusion de compte",
        from_email=settings.EMAIL_FROM,
        recipients=[merge_email],
        bindings={
            "CONFIRMATION_URL": confirm_merge_account,
            "REQUESTER_EMAIL": requester_email,
        },
    )


@emailing_task
def send_confirmation_change_email(new_email, user_pk, **kwargs):
    try:
        Person.objects.get(pk=user_pk)
    except Person.DoesNotExist:
        return

    subscription_token = add_email_confirmation_token_generator.make_token(
        new_email=new_email, user=user_pk
    )
    query_args = {
        "new_email": new_email,
        "user": user_pk,
        "token": subscription_token,
        **kwargs,
    }
    confirm_change_mail_url = front_url(
        "confirm_change_mail", query=query_args, auto_login=False
    )

    send_mosaico_email(
        code="CHANGE_MAIL_CONFIRMATION",
        subject="Confirmez votre changement d'adresse",
        from_email=settings.EMAIL_FROM,
        recipients=[new_email],
        bindings={"CONFIRMATION_URL": confirm_change_mail_url},
    )


@emailing_task
def send_unsubscribe_email(person_pk):
    person = Person.objects.prefetch_related("emails").get(pk=person_pk)

    bindings = {"MANAGE_SUBSCRIPTIONS_LINK": front_url("contact")}

    send_mosaico_email(
        code="UNSUBSCRIBE_CONFIRMATION",
        subject=_("Vous avez été désabonné⋅e des emails de la France insoumise"),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings,
    )


@emailing_task
def send_person_form_confirmation(submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except:
        return

    person = submission.person
    form = submission.form

    bindings = {"CONFIRMATION_NOTE": mark_safe(form.confirmation_note)}

    send_mosaico_email(
        code="FORM_CONFIRMATION",
        subject=_("Confirmation"),
        from_email=settings.EMAIL_FROM,
        recipients=[person],
        bindings=bindings,
    )


@emailing_task
def send_person_form_notification(submission_pk):
    try:
        submission = PersonFormSubmission.objects.get(pk=submission_pk)
    except:
        return

    form = submission.form

    if form.send_answers_to is None:
        return

    person = submission.person

    if person is None:
        # réponse anonyme au formulaire, pas d'email à qui envoyer
        return

    pretty_submission = default_person_form_display.get_formatted_submission(submission)

    bindings = {
        "ANSWER_EMAIL": person.email,
        "FORM_NAME": form.title,
        "INFORMATIONS": mark_safe(
            render_to_string(
                "people/includes/personform_submission_data.html",
                {"submission_data": pretty_submission},
            )
        ),
    }

    send_mosaico_email(
        code="FORM_NOTIFICATION",
        subject=_("Formulaire : " + form.title),
        from_email=settings.EMAIL_FROM,
        reply_to=[person.email],
        recipients=[form.send_answers_to],
        bindings=bindings,
    )


@shared_task
def send_validation_sms(sms_id):
    try:
        sms = PersonValidationSMS.objects.get(id=sms_id)
    except PersonValidationSMS.DoesNotExist:
        return

    formatted_code = sms.code[:3] + " " + sms.code[3:]
    message = f"Votre code de validation pour votre compte France insoumise est {formatted_code}"

    send_sms(message, sms.phone_number)


@shared_task
def notify_referrer(referrer_id, referred_id, referral_type):
    try:
        referrer = Person.objects.get(pk=referrer_id)
        referred = Person.objects.get(pk=referred_id)
    except (Person.DoesNotExist, TypeError, ValueError):
        # Ne pas oublier d'attraper les erreurs pour mauvais type ou mauvaise valeur
        return

    Activity.objects.create(
        recipient=referrer,
        type=Activity.TYPE_REFERRAL,
        status=Activity.STATUS_UNDISPLAYED,
        individual=referred,
        meta={
            "referralType": referral_type,
            "totalReferrals": Activity.objects.filter(
                recipient=referrer,
                type=Activity.TYPE_REFERRAL,
                meta__referalType=referral_type,
            ).count()
            + 1,
        },
    )
