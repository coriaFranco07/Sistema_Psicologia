from django.db import models

from . import CatalogoBaseModel


class Localidad(CatalogoBaseModel):
    id_localidad = models.AutoField(primary_key=True, db_column="id_localidad")
    dsc_localidad = models.CharField(max_length=150, db_column="dsc_localidad")

    class Meta:
        db_table = "localidad"
        ordering = ("dsc_localidad", "id_localidad")
        verbose_name = "localidad"
        verbose_name_plural = "localidades"

    def __str__(self):
        return self.dsc_localidad
