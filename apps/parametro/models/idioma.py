from django.db import models

from . import CatalogoBaseModel


class Idioma(CatalogoBaseModel):
    id_idioma = models.AutoField(primary_key=True, db_column="id_idioma")
    dsc_idioma = models.CharField(max_length=150, db_column="dsc_idioma")

    class Meta:
        db_table = "idioma"
        ordering = ("dsc_idioma", "id_idioma")
        verbose_name = "idioma"
        verbose_name_plural = "idiomas"

    def __str__(self):
        return self.dsc_idioma
