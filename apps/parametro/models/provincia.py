from django.db import models

from . import CatalogoBaseModel


class Provincia(CatalogoBaseModel):
    id_provincia = models.AutoField(primary_key=True, db_column="id_provincia")
    dsc_provincia = models.CharField(max_length=150, db_column="dsc_provincia")

    class Meta:
        db_table = "provincia"
        ordering = ("dsc_provincia", "id_provincia")
        verbose_name = "provincia"
        verbose_name_plural = "provincias"

    def __str__(self):
        return self.dsc_provincia


class PaisProvincia(CatalogoBaseModel):
    id_pais_provincia = models.AutoField(primary_key=True, db_column="id_pais_provincia")
    id_pais = models.ForeignKey(
        "parametro.Pais",
        on_delete=models.PROTECT,
        db_column="id_pais",
        related_name="pais_provincias",
    )
    id_provincia = models.ForeignKey(
        "parametro.Provincia",
        on_delete=models.PROTECT,
        db_column="id_provincia",
        related_name="provincia_paises",
    )

    class Meta:
        db_table = "pais_provincia"
        ordering = ("id_pais", "id_provincia", "id_pais_provincia")
        verbose_name = "pais provincia"
        verbose_name_plural = "paises provincias"
        constraints = [
            models.UniqueConstraint(
                fields=("id_pais", "id_provincia"),
                name="uq_pais_provincia",
            )
        ]

    def __str__(self):
        return f"{self.id_pais.dsc_pais} / {self.id_provincia.dsc_provincia}"


class ProvinciaLocalidad(CatalogoBaseModel):
    id_provincia_localidad = models.AutoField(primary_key=True, db_column="id_provincia_localidad")
    id_provincia = models.ForeignKey(
        "parametro.Provincia",
        on_delete=models.PROTECT,
        db_column="id_provincia",
        related_name="provincia_localidades",
    )
    id_localidad = models.ForeignKey(
        "parametro.Localidad",
        on_delete=models.PROTECT,
        db_column="id_localidad",
        related_name="localidad_provincias",
    )

    class Meta:
        db_table = "provincia_localidad"
        ordering = ("id_provincia", "id_localidad", "id_provincia_localidad")
        verbose_name = "provincia localidad"
        verbose_name_plural = "provincias localidades"
        constraints = [
            models.UniqueConstraint(
                fields=("id_provincia", "id_localidad"),
                name="uq_provincia_localidad",
            )
        ]

    def __str__(self):
        return f"{self.id_provincia.dsc_provincia} / {self.id_localidad.dsc_localidad}"
