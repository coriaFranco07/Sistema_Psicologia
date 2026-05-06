from django.db import IntegrityError, models
from apps.parametro.models.localidad import Localidad
from apps.parametro.models.pais import Pais
from apps.parametro.models.provincia import Provincia
from apps.parametro.models.tipo_civil import TipoCivil
from apps.parametro.models.zona import Zona
from apps.usuario.models import Usuario
from django.core.validators import MinValueValidator, MaxValueValidator
from simple_history.models import HistoricalRecords


class DatosPersonales(models.Model):
   username = models.ForeignKey(Usuario, on_delete=models.RESTRICT,related_name="usuario_datos")
   nro_socio = models.PositiveBigIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(999999)],
        unique=True,
        null=True,
        blank=True,
        db_index=True
   )
   telefono=models.CharField(null=False, blank=False,max_length=25)
   domicilio=models.CharField(null=False, blank=False,max_length=200)
   id_std_civil=models.ForeignKey(TipoCivil, null=False, blank=False,on_delete=models.RESTRICT)
   id_pais=models.ForeignKey(Pais, null=False, blank=False,on_delete=models.RESTRICT)
   id_provincia=models.ForeignKey(Provincia, null=False, blank=False,on_delete=models.RESTRICT)
   id_localidad=models.ForeignKey(Localidad, null=False, blank=False,on_delete=models.RESTRICT)
   id_zona=models.ForeignKey(Zona, null=False, blank=False, on_delete=models.RESTRICT)

   history = HistoricalRecords()
   
   class Meta:
        verbose_name='Dato Personal'
        verbose_name_plural='Datos Personales'
        ordering=['-nro_socio']
        

   def __str__(self) -> str:
       return f"DNI: {self.username.dni} - Nombres: {self.username.nombres} - Socio: {self.nro_socio} "
   

   def save(self, *args, **kwargs):
        if self.nro_socio:
            return super().save(*args, **kwargs)

        from apps.usuario.utils import obtener_nro_socio_disponible

        for _ in range(10):
            try:
                self.nro_socio = obtener_nro_socio_disponible()
                return super().save(*args, **kwargs)
            except IntegrityError:
                self.nro_socio = None

        raise IntegrityError("No se pudo generar nro_socio único")
   
