from django.db import models

from . import CatalogoBaseModel


class MetodoPago(CatalogoBaseModel):
    id_metodo_pago = models.AutoField(primary_key=True, db_column="id_metodo_pago")
    dsc_met_pago = models.CharField(max_length=150, db_column="dsc_met_pago")

    class Meta:
        db_table = "metodo_pago"
        ordering = ("dsc_met_pago", "id_metodo_pago")
        verbose_name = "metodo de pago"
        verbose_name_plural = "metodos de pago"

    def __str__(self):
        return self.dsc_met_pago
