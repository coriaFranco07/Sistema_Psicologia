from django.db import models

from . import CatalogoBaseModel


class Ocupacion(CatalogoBaseModel):
    id_ocupacion = models.AutoField(primary_key=True, db_column="id_ocupacion")
    dsc_ocupacion = models.CharField(max_length=150, db_column="dsc_ocupacion")

    class Meta:
        db_table = "ocupacion"
        ordering = ("dsc_ocupacion", "id_ocupacion")
        verbose_name = "ocupacion"
        verbose_name_plural = "ocupaciones"

    def __str__(self):
        return self.dsc_ocupacion
