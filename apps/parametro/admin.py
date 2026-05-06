from django.contrib import admin

from .models import (
    Estado,
    GradoEstudio,
    Idioma,
    Localidad,
    MetodoPago,
    Ocupacion,
    Pais,
    PaisProvincia,
    Provincia,
    ProvinciaLocalidad,
    Sexo,
    TipoCita,
    TipoCivil,
    Zona,
    ZonaLocalidad,
    CicloVida,
)


class BaseParametroAdmin(admin.ModelAdmin):
    list_filter = ("flg_activo",)
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    save_on_top = True


@admin.register(Sexo)
class SexoAdmin(BaseParametroAdmin):
    list_display = ("id_sexo", "dsc_tipo", "flg_activo")
    search_fields = ("dsc_tipo",)
    list_editable = ("dsc_tipo", "flg_activo")
    ordering = ("dsc_tipo", "id_sexo")


@admin.register(Idioma)
class IdiomaAdmin(BaseParametroAdmin):
    list_display = ("id_idioma", "dsc_idioma", "flg_activo")
    search_fields = ("dsc_idioma",)
    list_editable = ("dsc_idioma", "flg_activo")
    ordering = ("dsc_idioma", "id_idioma")


@admin.register(Estado)
class EstadoAdmin(BaseParametroAdmin):
    list_display = ("id_estado", "dsc_estado", "flg_activo")
    search_fields = ("dsc_estado",)
    list_editable = ("dsc_estado", "flg_activo")
    ordering = ("dsc_estado", "id_estado")


@admin.register(TipoCivil)
class TipoCivilAdmin(BaseParametroAdmin):
    list_display = ("id_estado_civil", "dsc_std_civil", "flg_activo")
    search_fields = ("dsc_std_civil",)
    list_editable = ("dsc_std_civil", "flg_activo")
    ordering = ("dsc_std_civil", "id_estado_civil")


@admin.register(MetodoPago)
class MetodoPagoAdmin(BaseParametroAdmin):
    list_display = ("id_metodo_pago", "dsc_met_pago", "flg_activo")
    search_fields = ("dsc_met_pago",)
    list_editable = ("dsc_met_pago", "flg_activo")
    ordering = ("dsc_met_pago", "id_metodo_pago")


@admin.register(TipoCita)
class TipoCitaAdmin(BaseParametroAdmin):
    list_display = ("id_tipo_cita", "dsc_t_cita", "flg_activo")
    search_fields = ("dsc_t_cita",)
    list_editable = ("dsc_t_cita", "flg_activo")
    ordering = ("dsc_t_cita", "id_tipo_cita")


@admin.register(Ocupacion)
class OcupacionAdmin(BaseParametroAdmin):
    list_display = ("id_ocupacion", "dsc_ocupacion", "flg_activo")
    search_fields = ("dsc_ocupacion",)
    list_editable = ("dsc_ocupacion", "flg_activo")
    ordering = ("dsc_ocupacion", "id_ocupacion")


@admin.register(GradoEstudio)
class GradoEstudioAdmin(BaseParametroAdmin):
    list_display = ("id_grado_estudio", "dsc_grado_estudio", "flg_activo")
    search_fields = ("dsc_grado_estudio",)
    list_editable = ("dsc_grado_estudio", "flg_activo")
    ordering = ("dsc_grado_estudio", "id_grado_estudio")


@admin.register(Pais)
class PaisAdmin(BaseParametroAdmin):
    list_display = ("id_pais", "dsc_pais", "flg_activo")
    search_fields = ("dsc_pais",)
    list_editable = ("dsc_pais", "flg_activo")
    ordering = ("dsc_pais", "id_pais")


@admin.register(Provincia)
class ProvinciaAdmin(BaseParametroAdmin):
    list_display = ("id_provincia", "dsc_provincia", "flg_activo")
    search_fields = ("dsc_provincia",)
    list_editable = ("dsc_provincia", "flg_activo")
    ordering = ("dsc_provincia", "id_provincia")


@admin.register(PaisProvincia)
class PaisProvinciaAdmin(BaseParametroAdmin):
    list_display = ("id_pais_provincia", "dsc_pais", "dsc_provincia", "flg_activo")
    search_fields = ("id_pais__dsc_pais", "id_provincia__dsc_provincia")
    list_editable = ("flg_activo",)
    ordering = ("id_pais__dsc_pais", "id_provincia__dsc_provincia", "id_pais_provincia")
    autocomplete_fields = ("id_pais", "id_provincia")
    list_select_related = ("id_pais", "id_provincia")

    @admin.display(ordering="id_pais__dsc_pais", description="Pais")
    def dsc_pais(self, obj):
        return obj.id_pais.dsc_pais

    @admin.display(ordering="id_provincia__dsc_provincia", description="Provincia")
    def dsc_provincia(self, obj):
        return obj.id_provincia.dsc_provincia


@admin.register(ProvinciaLocalidad)
class ProvinciaLocalidadAdmin(BaseParametroAdmin):
    list_display = ("id_provincia_localidad", "dsc_provincia", "dsc_localidad", "flg_activo")
    search_fields = ("id_provincia__dsc_provincia", "id_localidad__dsc_localidad")
    list_editable = ("flg_activo",)
    ordering = (
        "id_provincia__dsc_provincia",
        "id_localidad__dsc_localidad",
        "id_provincia_localidad",
    )
    autocomplete_fields = ("id_provincia", "id_localidad")
    list_select_related = ("id_provincia", "id_localidad")

    @admin.display(ordering="id_provincia__dsc_provincia", description="Provincia")
    def dsc_provincia(self, obj):
        return obj.id_provincia.dsc_provincia

    @admin.display(ordering="id_localidad__dsc_localidad", description="Localidad")
    def dsc_localidad(self, obj):
        return obj.id_localidad.dsc_localidad


@admin.register(Zona)
class ZonaAdmin(BaseParametroAdmin):
    list_display = ("id_zona", "dsc_zona", "flg_activo")
    search_fields = ("dsc_zona",)
    list_editable = ("dsc_zona", "flg_activo")
    ordering = ("dsc_zona", "id_zona")


@admin.register(Localidad)
class LocalidadAdmin(BaseParametroAdmin):
    list_display = ("id_localidad", "dsc_localidad", "flg_activo")
    search_fields = ("dsc_localidad",)
    list_editable = ("dsc_localidad", "flg_activo")
    ordering = ("dsc_localidad", "id_localidad")


@admin.register(ZonaLocalidad)
class ZonaLocalidadAdmin(BaseParametroAdmin):
    list_display = ("id_zona_localidad", "dsc_zona", "dsc_localidad", "flg_activo")
    search_fields = ("id_zona__dsc_zona", "id_localidad__dsc_localidad")
    list_editable = ("flg_activo",)
    ordering = ("id_zona__dsc_zona", "id_localidad__dsc_localidad", "id_zona_localidad")
    autocomplete_fields = ("id_zona", "id_localidad")
    list_select_related = ("id_zona", "id_localidad")

    @admin.display(ordering="id_zona__dsc_zona", description="Zona")
    def dsc_zona(self, obj):
        return obj.id_zona.dsc_zona

    @admin.display(ordering="id_localidad__dsc_localidad", description="Localidad")
    def dsc_localidad(self, obj):
        return obj.id_localidad.dsc_localidad


@admin.register(CicloVida)
class CicloVidaAdmin(BaseParametroAdmin):
    list_display = ("id_ciclo_vida", "dsc_ciclo_vida", "flg_activo")
    search_fields = ("dsc_ciclo_vida",)
    list_editable = ("dsc_ciclo_vida", "flg_activo")
    ordering = ("dsc_ciclo_vida", "id_ciclo_vida")