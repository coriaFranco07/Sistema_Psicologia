from django.db import models

from . import CatalogoBaseModel


class Zona(CatalogoBaseModel):
    id_zona = models.AutoField(primary_key=True, db_column="id_zona")
    dsc_zona = models.CharField(max_length=150, db_column="dsc_zona")

    class Meta:
        db_table = "zona"
        ordering = ("dsc_zona", "id_zona")
        verbose_name = "zona"
        verbose_name_plural = "zonas"

    def __str__(self):
        return self.dsc_zona


class ZonaLocalidad(CatalogoBaseModel):
    id_zona_localidad = models.AutoField(primary_key=True, db_column="id_zona_localidad")
    id_zona = models.ForeignKey(
        "parametro.Zona",
        on_delete=models.PROTECT,
        db_column="id_zona",
        related_name="zona_localidades",
    )
    id_localidad = models.ForeignKey(
        "parametro.Localidad",
        on_delete=models.PROTECT,
        db_column="id_localidad",
        related_name="localidad_zonas",
    )

    class Meta:
        db_table = "zona_localidad"
        ordering = ("id_zona", "id_localidad", "id_zona_localidad")
        verbose_name = "zona localidad"
        verbose_name_plural = "zona localidades"
        constraints = [
            models.UniqueConstraint(
                fields=("id_zona", "id_localidad"),
                name="uq_zona_localidad",
            )
        ]

    def __str__(self):
        return f"{self.id_zona.dsc_zona} / {self.id_localidad.dsc_localidad}"
