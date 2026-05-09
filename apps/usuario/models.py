from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import (
    FileExtensionValidator,
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.templatetags.static import static

from apps.parametro.models import (
    CicloVida,
    Estado,
    GradoEstudio,
    Localidad,
    Ocupacion,
    Pais,
    Provincia,
    Rama,
    Sexo,
    TipoCivil,
    Zona,
)


MAX_SIZE_MB = 5
CICLO_VIDA_POR_EDAD = (
    (11, "INFANCIA"),
    (18, "ADOLESCENCIA"),
    (40, "ADULTEZ INICIAL"),
    (60, "ADULTEZ MADURA"),
)


def validate_photo_size(file_obj):
    if not file_obj:
        return

    max_size = MAX_SIZE_MB * 1024 * 1024
    if file_obj.size > max_size:
        raise ValidationError(f"La foto no puede superar los {MAX_SIZE_MB} MB.")


def calculate_age_from_birth_date(fch_nacimiento, today=None):
    if not fch_nacimiento:
        return None

    today = today or date.today()
    return today.year - fch_nacimiento.year - (
        (today.month, today.day) < (fch_nacimiento.month, fch_nacimiento.day)
    )


class UsuarioBase(models.Model):
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
    def edad(self):
        return calculate_age_from_birth_date(self.fch_nacimiento)

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


class Psicologo(UsuarioBase):

    id_rama = models.ForeignKey(Rama, on_delete=models.RESTRICT, related_name="psicologos", verbose_name="Rama")
    titulo = models.FileField(
        upload_to="psicologos/titulos/",
        default="",
        verbose_name="Titulo",
        validators=[FileExtensionValidator(["pdf"])],
    )

    class Meta(UsuarioBase.Meta):
        verbose_name = "Psicologo"
        verbose_name_plural = "Psicologos"


class PsicologoPendiente(models.Model):
    ESTADO_PENDIENTE = "PENDIENTE"
    ESTADO_APROBADO = "APROBADO"
    ESTADO_RECHAZADO = "RECHAZADO"
    ESTADOS = (
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_APROBADO, "Aprobado"),
        (ESTADO_RECHAZADO, "Rechazado"),
    )

    nombres = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    dni = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1_000_000), MaxValueValidator(99_999_999)]
    )
    cuil = models.PositiveBigIntegerField(
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
    id_rama = models.ForeignKey(
        Rama,
        on_delete=models.RESTRICT,
        related_name="psicologos_pendientes",
        verbose_name="Rama",
    )
    titulo = models.FileField(
        upload_to="psicologos/titulos/",
        verbose_name="Titulo",
        validators=[FileExtensionValidator(["pdf"])],
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
    password_hash = models.CharField(max_length=128)
    estado = models.CharField(
        max_length=12,
        choices=ESTADOS,
        default=ESTADO_PENDIENTE,
    )
    psicologo = models.OneToOneField(
        Psicologo,
        on_delete=models.SET_NULL,
        related_name="solicitud_origen",
        null=True,
        blank=True,
    )
    fch_creacion = models.DateTimeField(auto_now_add=True)
    fch_actualizacion = models.DateTimeField(auto_now=True)
    fch_resolucion = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-fch_creacion",)
        verbose_name = "Psicologo pendiente"
        verbose_name_plural = "Psicologos pendientes"

    def __str__(self):
        return f"{self.nombres} - DNI {self.dni} ({self.get_estado_display()})"

    @property
    def edad(self):
        return calculate_age_from_birth_date(self.fch_nacimiento)

    @property
    def foto_url(self):
        if self.foto:
            return self.foto.url
        return static("images/foto_usuario_default.png")


class Paciente(UsuarioBase):
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

    class Meta(UsuarioBase.Meta):
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    @classmethod
    def get_ciclo_vida_descripcion_by_age(cls, edad):
        if edad is None or edad < 0:
            return None

        for edad_maxima, descripcion in CICLO_VIDA_POR_EDAD:
            if edad < edad_maxima:
                return descripcion
        return "VEJEZ"

    def assign_ciclo_vida_from_birth_date(self):
        descripcion = self.get_ciclo_vida_descripcion_by_age(self.edad)
        if not descripcion:
            return None

        ciclo_vida = (
            CicloVida.objects.filter(dsc_ciclo_vida__iexact=descripcion, flg_activo=True)
            .order_by("id_ciclo_vida")
            .first()
        )
        if ciclo_vida is None:
            raise ValidationError(
                {
                    "fch_nacimiento": (
                        f"No existe un ciclo de vida activo configurado para '{descripcion}'."
                    )
                }
            )

        self.id_ciclo_vida = ciclo_vida
        return ciclo_vida

    def clean(self):
        super().clean()
        if self.fch_nacimiento:
            self.assign_ciclo_vida_from_birth_date()

    def save(self, *args, **kwargs):
        if self.fch_nacimiento:
            self.assign_ciclo_vida_from_birth_date()
        super().save(*args, **kwargs)
