from django.db import models
from simple_history.models import HistoricalRecords
from apps.usuario.models import Usuario


class Modulo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    codigo = models.CharField(max_length=50, unique=True)
    activo = models.BooleanField(default=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.nombre


class PermisoModulo(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='permisos_modulo')
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='permisos')
    puede_ver = models.BooleanField(default=False)
    puede_editar = models.BooleanField(default=False)
    puede_eliminar = models.BooleanField(default=False)
    puede_agregar = models.BooleanField(default=False)

    history = HistoricalRecords()

    class Meta:
        unique_together = ('usuario', 'modulo')

    def __str__(self):
        return f"{self.usuario.username} - {self.modulo.nombre}"
