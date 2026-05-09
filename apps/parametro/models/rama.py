from django.db import models

from . import CatalogoBaseModel


class Rama(CatalogoBaseModel):
    id_rama = models.AutoField(primary_key=True, db_column="id_rama")
    dsc_rama = models.CharField(max_length=150, db_column="dsc_rama")

    class Meta:
        db_table = "rama"
        ordering = ("dsc_rama", "id_rama")
        verbose_name = "rama"
        verbose_name_plural = "ramas"

    def __str__(self):
        return self.dsc_rama
