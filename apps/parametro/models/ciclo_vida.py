from django.db import models
from . import CatalogoBaseModel


class CicloVida(CatalogoBaseModel):
    id_ciclo_vida = models.AutoField(primary_key=True, db_column="id_ciclo_vida")
    dsc_ciclo_vida = models.CharField(max_length=150, db_column="dsc_ciclo_vida")

    class Meta:
        db_table = "ciclo_vida"
        ordering = ("dsc_ciclo_vida", "id_ciclo_vida")
        verbose_name = "ciclo de vida"
        verbose_name_plural = "ciclos de vida"

    def __str__(self):
        return self.dsc_ciclo_vida