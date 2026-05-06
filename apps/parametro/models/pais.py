from django.db import models

from . import CatalogoBaseModel


class Pais(CatalogoBaseModel):
    id_pais = models.AutoField(primary_key=True, db_column="id_pais")
    dsc_pais = models.CharField(max_length=150, db_column="dsc_pais")

    class Meta:
        db_table = "pais"
        ordering = ("dsc_pais", "id_pais")
        verbose_name = "pais"
        verbose_name_plural = "paises"

    def __str__(self):
        return self.dsc_pais
