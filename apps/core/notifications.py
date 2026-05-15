import logging
from email.mime.image import MIMEImage
from pathlib import Path

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


logger = logging.getLogger(__name__)

EMAIL_LOGO_CID = "menteclara-logo"


def _logo_path():
    return Path(settings.BASE_DIR) / "static" / "images" / "MenteClara_sinFondo.png"


def _attach_logo(message):
    logo_path = _logo_path()
    if not logo_path.exists():
        return

    logo = MIMEImage(logo_path.read_bytes())
    logo.add_header("Content-ID", f"<{EMAIL_LOGO_CID}>")
    logo.add_header("Content-Disposition", "inline", filename=logo_path.name)
    message.attach(logo)


def send_branded_email(*, to_email, subject, heading, intro, body_lines, footer_note, cta_label=None, cta_url=None):
    if not to_email:
        return False

    context = {
        "heading": heading,
        "intro": intro,
        "body_lines": body_lines,
        "footer_note": footer_note,
        "cta_label": cta_label,
        "cta_url": cta_url,
        "logo_cid": EMAIL_LOGO_CID,
    }
    text_body = "\n".join([heading, "", intro, "", *body_lines, "", footer_note])
    html_body = render_to_string("emails/branded_notification.html", context)

    try:
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.CORREO_OFICIAL,
            to=[to_email],
        )
        message.attach_alternative(html_body, "text/html")
        _attach_logo(message)
        message.send(fail_silently=False)
        return True
    except Exception:
        logger.exception("No se pudo enviar el correo a %s", to_email)
        return False


def send_profile_submission_email(*, to_email, full_name, profile_type):
    return send_branded_email(
        to_email=to_email,
        subject=f"Recibimos tu solicitud en MenteClara, {full_name}",
        heading="Tu solicitud está siendo analizada",
        intro=f"Hola {full_name}, recibimos correctamente tu solicitud de {profile_type}.",
        body_lines=[
            "Nuestro equipo ya está revisando tus datos.",
            "En unos minutos se dará de alta tu perfil si todo está correcto.",
            "Te vamos a notificar por este mismo correo cuando el proceso esté aprobado.",
        ],
        footer_note="Gracias por elegir MenteClara.",
    )


def send_profile_approved_email(*, to_email, full_name, profile_type, login_url):
    return send_branded_email(
        to_email=to_email,
        subject=f"Tu perfil en MenteClara fue aprobado, {full_name}",
        heading="Tu perfil ya fue aprobado",
        intro=f"Hola {full_name}, tu solicitud de {profile_type} fue aprobada con éxito.",
        body_lines=[
            "Ya puedes ingresar a la plataforma con tu DNI y la contraseña que registraste.",
            "Tu espacio en MenteClara está listo para usarse.",
        ],
        footer_note="Si no reconoces esta solicitud, por favor responde a este correo.",
        cta_label="Ingresar al sistema",
        cta_url=login_url,
    )
