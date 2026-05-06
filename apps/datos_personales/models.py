from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from apps.parametro.models import Localidad, Pais, Provincia, Sexo, TipoCivil, Zona
from apps.usuario.models import Paciente, Psicologo


class DatosPersonales(models.Model):
    psicologo = models.OneToOneField(
        Psicologo,
        on_delete=models.CASCADE,
        related_name="datos_personales",
        null=True,
        blank=True,
    )
    paciente = models.OneToOneField(
        Paciente,
        on_delete=models.CASCADE,
        related_name="datos_personales",
        null=True,
        blank=True,
    )
    telefono = models.CharField(max_length=25)
    domicilio = models.CharField(max_length=200)
    id_sexo = models.ForeignKey(Sexo, on_delete=models.RESTRICT, verbose_name="Sexo")
    id_std_civil = models.ForeignKey(
        TipoCivil,
        on_delete=models.RESTRICT,
        verbose_name="Estado civil",
    )
    id_pais = models.ForeignKey(Pais, on_delete=models.RESTRICT, verbose_name="Pais")
    id_provincia = models.ForeignKey(
        Provincia,
        on_delete=models.RESTRICT,
        verbose_name="Provincia",
    )
    id_localidad = models.ForeignKey(
        Localidad,
        on_delete=models.RESTRICT,
        verbose_name="Localidad",
    )
    id_zona = models.ForeignKey(Zona, on_delete=models.RESTRICT, verbose_name="Zona")
    fch_creacion = models.DateTimeField(auto_now_add=True)
    fch_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dato personal"
        verbose_name_plural = "Datos personales"
        ordering = ("-fch_actualizacion",)
        constraints = [
            models.CheckConstraint(
                check=(
                    (Q(psicologo__isnull=False) & Q(paciente__isnull=True))
                    | (Q(psicologo__isnull=True) & Q(paciente__isnull=False))
                ),
                name="datos_personales_una_sola_persona",
            )
        ]

    def clean(self):
        super().clean()
        if bool(self.psicologo) == bool(self.paciente):
            raise ValidationError(
                "Los datos personales deben estar asociados a un psicologo o a un paciente."
            )

    @property
    def persona(self):
        return self.psicologo or self.paciente

    def __str__(self):
        persona = self.persona
        if not persona:
            return "Datos personales sin asociar"
        return f"{persona.nombres} - DNI {persona.dni}"
