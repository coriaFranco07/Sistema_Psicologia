from django.db import models

from . import CatalogoBaseModel


class Sexo(CatalogoBaseModel):
    id_sexo = models.AutoField(primary_key=True, db_column="id_sexo")
    dsc_tipo = models.CharField(max_length=150, db_column="dsc_tipo")

    class Meta:
        db_table = "sexo"
        ordering = ("dsc_tipo", "id_sexo")
        verbose_name = "sexo"
        verbose_name_plural = "sexos"

    def __str__(self):
        return self.dsc_tipo
