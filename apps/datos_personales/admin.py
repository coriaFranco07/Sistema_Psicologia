from django.contrib import admin
from .models import DatosPersonales, DatosPersonalesPendiente, Jerarquia, Pais,Provincia, Localidad,EstadoCivil

from apps.usuario.models import Usuario
from .models import EstadoCivil, Pais, Localidad, Provincia, Zona


class DatosPersonalesAdmin(DatosPersonales):
    model = DatosPersonales
    list_display = ('username','nro_socio', 'telefono','id_std_civil', 'domicilio','id_localidad','id_provincia','id_pais','id_zona')
    search_fields = ('username__dni',)
    ordering = ('username__nombres',)


@admin.register(Jerarquia)
class JerarquiaAdmin(admin.ModelAdmin):
    list_display = ('dsc_jerarquia', 'nivel')
    ordering = ('nivel',)


# Register your models here.
admin.site.register([DatosPersonales, Pais, Localidad, Provincia, EstadoCivil, Zona, DatosPersonalesPendiente])
