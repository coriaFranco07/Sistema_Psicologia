from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.templatetags.static import static

from apps.parametro.models import CicloVida, Estado, GradoEstudio, Ocupacion


MAX_SIZE_MB = 5


def validate_photo_size(file_obj):
    if not file_obj:
        return

    max_size = MAX_SIZE_MB * 1024 * 1024
    if file_obj.size > max_size:
        raise ValidationError(f"La foto no puede superar los {MAX_SIZE_MB} MB.")


class PersonaBase(models.Model):
    nombres = models.CharField(max_length=100)
    email = models.EmailField(max_length=50, unique=True)
    dni = models.PositiveBigIntegerField(
        unique=True,
        validators=[MinValueValidator(1_000_000), MaxValueValidator(99_999_999)],
    )
    cuil = models.PositiveBigIntegerField(
        unique=True,
        null=True,
        blank=True,
        validators=[MinValueValidator(10_000_000_000), MaxValueValidator(99_999_999_999)],
    )
    fch_nacimiento = models.DateField(verbose_name="Fecha de nacimiento")
    foto = models.FileField(
        upload_to="personas/fotos/",
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(["jpg", "jpeg", "png", "webp"]),
            validate_photo_size,
        ],
    )
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        related_name="%(class)ss",
        verbose_name="Estado",
    )
    fch_creacion = models.DateTimeField(auto_now_add=True)
    fch_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ("nombres", "dni")

    def clean(self):
        super().clean()
        if self.cuil:
            cuil = str(self.cuil)
            dni = str(self.dni).zfill(8)
            if len(cuil) != 11:
                raise ValidationError({"cuil": "El CUIL debe tener 11 dígitos."})
            if cuil[2:10] != dni:
                raise ValidationError(
                    {"cuil": "Los dígitos centrales del CUIL deben coincidir con el DNI."}
                )

    def __str__(self):
        return f"{self.nombres} - DNI {self.dni}"

    @property
    def foto_url(self):
        if self.foto:
            return self.foto.url
        return static("images/foto_usuario_default.png")

    @property
    def datos_personales_rel(self):
        try:
            return self.datos_personales
        except Exception:
            return None


class Psicologo(PersonaBase):
    class Meta(PersonaBase.Meta):
        verbose_name = "Psicologo"
        verbose_name_plural = "Psicologos"


class Paciente(PersonaBase):
    id_ocupacion = models.ForeignKey(
        Ocupacion,
        on_delete=models.RESTRICT,
        related_name="pacientes",
        verbose_name="Ocupacion",
    )
    id_ciclo_vida = models.ForeignKey(
        CicloVida,
        on_delete=models.RESTRICT,
        related_name="pacientes",
        verbose_name="Ciclo de vida",
    )
    id_grado_estudio = models.ForeignKey(
        GradoEstudio,
        on_delete=models.RESTRICT,
        related_name="pacientes",
        verbose_name="Grado de estudio",
    )

    class Meta(PersonaBase.Meta):
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
