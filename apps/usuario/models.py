from datetime import date
from decimal import Decimal

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
from apps.parametro.models.idioma import Idioma
from apps.parametro.models.metodo_pago import MetodoPago


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
    titulo = models.FileField(
        upload_to="psicologos/titulos/",
        default="",
        verbose_name="Titulo",
        validators=[FileExtensionValidator(["pdf"])],
    )

    class Meta(UsuarioBase.Meta):
        verbose_name = "Psicologo"
        verbose_name_plural = "Psicologos"

    def __init__(self, *args, **kwargs):
        self._pending_id_rama = kwargs.pop("id_rama", None)
        self._pending_valor_sesion = kwargs.pop("valor_sesion", None)
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_default_rama_estado():
        return Estado.objects.filter(dsc_estado__iexact="ACTIVO", flg_activo=True).first()

    def get_ramas_activas(self):
        if not self.pk:
            return []

        ramas_prefetch = getattr(self, "ramas_activas", None)
        if ramas_prefetch is not None:
            return ramas_prefetch

        return list(
            self.ramas.select_related("id_rama", "id_estado")
            .filter(id_estado__dsc_estado__iexact="ACTIVO", id_estado__flg_activo=True)
            .order_by("id_psico_rama")
        )

    @property
    def rama_principal_rel(self):
        if not self.pk:
            return None

        ramas = self.get_ramas_activas()
        if ramas:
            return ramas[0]

        return (
            self.ramas.select_related("id_rama", "id_estado")
            .order_by("id_psico_rama")
            .first()
        )

    @property
    def id_rama(self):
        rama_principal = self.rama_principal_rel
        return rama_principal.id_rama if rama_principal else None

    @id_rama.setter
    def id_rama(self, value):
        self._pending_id_rama = value

    @property
    def valor_sesion(self):
        rama_principal = self.rama_principal_rel
        return rama_principal.valor_sesion if rama_principal else Decimal("0.00")

    @valor_sesion.setter
    def valor_sesion(self, value):
        self._pending_valor_sesion = value

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self._pending_id_rama is None and self._pending_valor_sesion is None:
            return

        rama_relacion = self.ramas.order_by("id_psico_rama").first()

        rama = self._pending_id_rama
        if rama is None and rama_relacion is not None:
            rama = rama_relacion.id_rama

        if rama is None:
            self._pending_valor_sesion = None
            return

        if isinstance(rama, int):
            rama = Rama.objects.get(pk=rama)

        valor_sesion = self._pending_valor_sesion
        if valor_sesion in (None, ""):
            valor_sesion = (
                rama_relacion.valor_sesion if rama_relacion is not None else Decimal("0.00")
            )

        estado = (
            rama_relacion.id_estado
            if rama_relacion is not None
            else self.get_default_rama_estado()
        )

        if rama_relacion is None and estado is None:
            self._pending_id_rama = None
            self._pending_valor_sesion = None
            return

        if rama_relacion is None:
            PsicologoRama.objects.create(
                id_psicologo=self,
                id_rama=rama,
                valor_sesion=valor_sesion,
                id_estado=estado,
            )
        else:
            rama_relacion.id_rama = rama
            rama_relacion.valor_sesion = valor_sesion
            rama_relacion.id_estado = estado
            rama_relacion.save(update_fields=["id_rama", "valor_sesion", "id_estado"])

        if hasattr(self, "ramas_activas"):
            delattr(self, "ramas_activas")

        self._pending_id_rama = None
        self._pending_valor_sesion = None


class PsicologoRama(models.Model):
    id_psico_rama = models.AutoField(primary_key=True, db_column="id_psico_rama")
    id_psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name="ramas",
        verbose_name="Psicologo",
    )
    id_rama = models.ForeignKey(
        Rama,
        on_delete=models.RESTRICT,
        related_name="psicologo_ramas",
        verbose_name="Rama",
    )
    valor_sesion = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name="Valor de sesion",
    )
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        related_name="psicologo_ramas",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Rama del psicologo"
        verbose_name_plural = "Ramas de los psicologos"
        constraints = [
            models.UniqueConstraint(
                fields=("id_psicologo", "id_rama"),
                name="uniq_psicologo_rama",
            )
        ]

    def __str__(self):
        return f"{self.id_psicologo.nombres} - {self.id_rama.dsc_rama}"


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

    def __init__(self, *args, **kwargs):
        self._pending_ramas = kwargs.pop("ramas_seleccionadas", None)
        rama_inicial = kwargs.pop("id_rama", None)
        if rama_inicial is not None and self._pending_ramas is None:
            self._pending_ramas = self.normalize_rama_ids([rama_inicial])
        super().__init__(*args, **kwargs)

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

    @staticmethod
    def normalize_rama_ids(ramas):
        if ramas is None:
            return None

        rama_ids = []
        vistos = set()
        for rama in ramas:
            rama_id = rama.pk if isinstance(rama, Rama) else int(rama)
            if rama_id in vistos:
                continue
            vistos.add(rama_id)
            rama_ids.append(rama_id)
        return rama_ids

    def set_ramas_pendientes(self, ramas):
        self._pending_ramas = self.normalize_rama_ids(ramas)

    def get_ramas_pendientes(self):
        if not self.pk:
            if self._pending_ramas is None:
                return []
            ramas_map = Rama.objects.in_bulk(self._pending_ramas)
            return [ramas_map[rama_id] for rama_id in self._pending_ramas if rama_id in ramas_map]

        relaciones_prefetch = getattr(self, "ramas_pendientes_prefetch", None)
        if relaciones_prefetch is not None:
            return [relacion.id_rama for relacion in relaciones_prefetch]

        return [
            relacion.id_rama
            for relacion in self.ramas_pendientes.select_related("id_rama").order_by(
                "id_psico_pend_rama"
            )
        ]

    @property
    def id_rama(self):
        ramas = self.get_ramas_pendientes()
        return ramas[0] if ramas else None

    @id_rama.setter
    def id_rama(self, value):
        self.set_ramas_pendientes([value] if value else [])

    @property
    def valor_sesion(self):
        return Decimal("0.00")

    @property
    def ramas_descripcion(self):
        ramas = self.get_ramas_pendientes()
        if not ramas:
            return "-"
        return ", ".join(rama.dsc_rama for rama in ramas)

    def sync_pending_ramas(self):
        if self._pending_ramas is None or not self.pk:
            return

        self._pending_ramas = self.normalize_rama_ids(self._pending_ramas)
        self.ramas_pendientes.all().delete()
        if self._pending_ramas:
            PsicologoPendienteRama.objects.bulk_create(
                [
                    PsicologoPendienteRama(
                        id_psicologo_pendiente=self,
                        id_rama_id=rama_id,
                    )
                    for rama_id in self._pending_ramas
                ]
            )

        if hasattr(self, "ramas_pendientes_prefetch"):
            delattr(self, "ramas_pendientes_prefetch")

        self._pending_ramas = None

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.sync_pending_ramas()


class PsicologoPendienteRama(models.Model):
    id_psico_pend_rama = models.AutoField(primary_key=True, db_column="id_psico_pend_rama")
    id_psicologo_pendiente = models.ForeignKey(
        PsicologoPendiente,
        on_delete=models.CASCADE,
        related_name="ramas_pendientes",
        verbose_name="Solicitud de psicologo",
    )
    id_rama = models.ForeignKey(
        Rama,
        on_delete=models.RESTRICT,
        related_name="psicologo_pendiente_ramas",
        verbose_name="Rama",
    )

    class Meta:
        verbose_name = "Rama seleccionada en solicitud"
        verbose_name_plural = "Ramas seleccionadas en solicitudes"
        constraints = [
            models.UniqueConstraint(
                fields=("id_psicologo_pendiente", "id_rama"),
                name="uniq_psicologo_pendiente_rama",
            )
        ]

    def __str__(self):
        return f"{self.id_psicologo_pendiente.nombres} - {self.id_rama.dsc_rama}"


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


class PsicologoMetodoPago(models.Model):
    
    id_psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name="metodos_pago",
        verbose_name="Psicologo",
    )
    
    id_metodo_pago = models.ForeignKey(MetodoPago, on_delete=models.RESTRICT, verbose_name="Método de pago")

    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        related_name="psicologo_metodo_pago",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Método de pago del psicólogo"
        verbose_name_plural = "Métodos de pago de los psicólogos"

    def __str__(self):
        return f"{self.id_psicologo.nombres} - {self.id_metodo_pago.dsc_met_pago}"
    

class PsicologoOficina(models.Model):
    id_psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name="oficinas",
        verbose_name="Psicologo",
    )
    domicilio = models.CharField(max_length=200, verbose_name="Domicilio")
    telefono = models.CharField(max_length=25, verbose_name="Teléfono")
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
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        related_name="psicologo_oficina",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Oficina del psicólogo"
        verbose_name_plural = "Oficinas de los psicólogos"

    def __str__(self):
        return f"{self.id_psicologo.nombres} - {self.domicilio}"
    


class PsicologoIdioma(models.Model):
    id_psicologo = models.ForeignKey(
        Psicologo,
        on_delete=models.CASCADE,
        related_name="idiomas",
        verbose_name="Psicologo",
    )
    id_idioma = models.ForeignKey(
        Idioma,
        on_delete=models.RESTRICT,
        verbose_name="Idioma",
    )
    id_estado = models.ForeignKey(
        Estado,
        on_delete=models.RESTRICT,
        related_name="psicologo_idioma",
        verbose_name="Estado",
    )

    class Meta:
        verbose_name = "Idioma del psicólogo"
        verbose_name_plural = "Idiomas de los psicólogos"

    def __str__(self):
        return f"{self.id_psicologo.nombres} - {self.id_idioma.dsc_idioma}"
