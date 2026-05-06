from django.db import models

from . import CatalogoBaseModel


class TipoCita(CatalogoBaseModel):
    id_tipo_cita = models.AutoField(primary_key=True, db_column="id_tipo_cita")
    dsc_t_cita = models.CharField(max_length=150, db_column="dsc_t_cita")

    class Meta:
        db_table = "tipo_cita"
        ordering = ("dsc_t_cita", "id_tipo_cita")
        verbose_name = "tipo de cita"
        verbose_name_plural = "tipos de cita"

    def __str__(self):
        return self.dsc_t_cita
