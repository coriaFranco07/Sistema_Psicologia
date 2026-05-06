from django.db import models
from datetime import timedelta
from django.utils import timezone
from apps.usuario.models import Usuario
from principal import settings

class LogSistema(models.Model):

    NIVELES = [
        ('INFO', 'INFO'),
        ('WARNING', 'WARNING'),
        ('ERROR', 'ERROR'),
        ('CRITICAL', 'CRITICAL'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Usuario logueado"
    )

    fecha_hora = models.DateTimeField(
        default=timezone.now,
        verbose_name="Fecha y hora"
    )

    nivel = models.CharField(
        max_length=20,
        choices=NIVELES,
        default='ERROR'
    )

    mensaje = models.TextField(
        verbose_name="Mensaje humano"
    )

    detalle = models.TextField(
        blank=True,
        null=True,
        verbose_name="Traceback técnico"
    )

    ruta = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Archivo y función"
    )

    metodo_http = models.CharField(
        max_length=10,
        blank=True,
        null=True
    )

    url = models.TextField(
        blank=True,
        null=True
    )

    ip_cliente = models.GenericIPAddressField(
        blank=True,
        null=True
    )

    modulo = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="App o módulo origen"
    )

    class Meta:
        verbose_name = "Log del Sistema"
        verbose_name_plural = "Logs del Sistema"
        ordering = ['-fecha_hora']

    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else "Anonimo"
        return f"[{self.nivel}] {usuario_str} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M:%S')}"

