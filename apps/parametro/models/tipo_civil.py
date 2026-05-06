from django.db import models

from . import CatalogoBaseModel


class TipoCivil(CatalogoBaseModel):
    id_estado_civil = models.AutoField(primary_key=True, db_column="id_estado_civil")
    dsc_std_civil = models.CharField(max_length=150, db_column="dsc_std_civil")

    class Meta:
        db_table = "tipo_civil"
        ordering = ("dsc_std_civil", "id_estado_civil")
        verbose_name = "tipo civil"
        verbose_name_plural = "tipos civiles"

    def __str__(self):
        return self.dsc_std_civil
