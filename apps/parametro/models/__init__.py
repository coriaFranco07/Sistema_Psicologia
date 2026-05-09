from django.db import models


class UpperCaseModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        for field in self._meta.fields:
            if field.name.startswith("dsc_"):
                value = getattr(self, field.name)
                if isinstance(value, str):
                    setattr(self, field.name, value.upper())
        super().save(*args, **kwargs)


class CatalogoBaseModel(UpperCaseModel):
    flg_activo = models.BooleanField(db_column="flg_activo", default=True)
    created_at = models.DateTimeField(db_column="created_at", auto_now_add=True)
    updated_at = models.DateTimeField(db_column="updated_at", auto_now=True)

    class Meta:
        abstract = True


from .ciclo_vida import CicloVida
from .estado import Estado
from .grado_estudio import GradoEstudio
from .idioma import Idioma
from .localidad import Localidad
from .metodo_pago import MetodoPago
from .ocupacion import Ocupacion
from .pais import Pais
from .provincia import PaisProvincia, Provincia, ProvinciaLocalidad
from .rama import Rama
from .sexo import Sexo
from .tipo_cita import TipoCita
from .tipo_civil import TipoCivil
from .zona import Zona, ZonaLocalidad

__all__ = [
    "CatalogoBaseModel",
    "CicloVida",
    "Estado",
    "GradoEstudio",
    "Idioma",
    "Localidad",
    "MetodoPago",
    "Ocupacion",
    "Pais",
    "PaisProvincia",
    "Provincia",
    "ProvinciaLocalidad",
    "Rama",
    "Sexo",
    "TipoCita",
    "TipoCivil",
    "UpperCaseModel",
    "Zona",
    "ZonaLocalidad",
]
