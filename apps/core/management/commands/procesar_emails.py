from django.core.management.base import BaseCommand
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage, get_connection
from django.conf import settings
from apps.core.models import ColaEmail
from apps.core.utils import log_error

LIMITE_DIARIO = 400  # LIMITE PARA CUENTA FREE 500.

class Command(BaseCommand):
    help = "Procesa la cola de emails"
    print("--- Iniciando Proceso-------")
    def handle(self, *args, **kwargs):

        hoy = timezone.localdate()
        print(f"--- Procesando emails {hoy} -------")

        # Agrupar por provider (cada gmail separado)
        providers = ["gmail_cuotas", "gmail_pagos", "gmail_sistema"]

        for provider in providers:
            print(f"------ PROVIDERS {provider}------")
            enviados_hoy = ColaEmail.objects.filter(
                provider=provider,
                estado="enviado",
                fecha_envio__date=hoy
            ).count()

            disponibles = LIMITE_DIARIO - enviados_hoy

            if disponibles <= 0:
                continue

            pendientes = (
                ColaEmail.objects
                .filter(
                    provider=provider,
                    estado="pendiente"
                )
                .order_by("prioridad", "fecha_programada")[:disponibles]
            )

            for email_obj in pendientes:
                try:
                    print(f"------ Destino: {email_obj.email_destino} ------")
                    if disponibles <= 0:
                        break

                    body = render_to_string(
                        email_obj.template,
                        email_obj.contexto
                    )

                    config = settings.EMAIL_PROVIDERS[email_obj.provider]

                    email = EmailMessage(
                        subject=email_obj.asunto,
                        body=body,
                        from_email=config["DEFAULT_FROM_EMAIL"],
                        to=[email_obj.email_destino],
                    )
                    email.content_subtype = "html"

                    if email_obj.adjunto:
                        email.attach_file(email_obj.adjunto.path)

                    # Conectarse al SMTP correcto
                    email.backend = "django.core.mail.backends.smtp.EmailBackend"
                    email.connection = get_connection(
                        host=config["EMAIL_HOST"],
                        port=config["EMAIL_PORT"],
                        username=config["EMAIL_HOST_USER"],
                        password=config["EMAIL_HOST_PASSWORD"],
                        use_tls=config["EMAIL_USE_TLS"]
                    )

                    email.send()

                    email_obj.estado = "enviado"
                    email_obj.fecha_envio = timezone.now()
                    email_obj.save()

                    disponibles -= 1

                except Exception as e:
                    email_obj.estado = "fallido"
                    email_obj.intentos += 1
                    email_obj.error = str(e)

                    log_error(
                        mensaje=f"Error al enviar email: {str(e)}"
                    )

                    email_obj.save()
                    disponibles -= 1
            
        print("--- FIN ENVIO DE MAILS.-------")