from django.db import models

from . import CatalogoBaseModel


class Estado(CatalogoBaseModel):
    id_estado = models.AutoField(primary_key=True, db_column="id_estado")
    dsc_estado = models.CharField(max_length=150, db_column="dsc_estado")

    class Meta:
        db_table = "estado"
        ordering = ("dsc_estado", "id_estado")
        verbose_name = "estado"
        verbose_name_plural = "estados"

    def __str__(self):
        return self.dsc_estado
