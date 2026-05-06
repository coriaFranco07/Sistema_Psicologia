from django.db import models

from . import CatalogoBaseModel


class GradoEstudio(CatalogoBaseModel):
    id_grado_estudio = models.AutoField(primary_key=True, db_column="id_grado_estudio")
    dsc_grado_estudio = models.CharField(max_length=150, db_column="dsc_grado_estudio")

    class Meta:
        db_table = "grado_estudio"
        ordering = ("dsc_grado_estudio", "id_grado_estudio")
        verbose_name = "grado de estudio"
        verbose_name_plural = "grados de estudio"

    def __str__(self):
        return self.dsc_grado_estudio
