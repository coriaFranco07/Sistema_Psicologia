from django.contrib import admin

from .models import DatosPersonales


@admin.register(DatosPersonales)
class DatosPersonalesAdmin(admin.ModelAdmin):
    list_display = (
        "persona_display",
        "telefono",
        "id_sexo",
        "id_std_civil",
        "id_localidad",
        "id_provincia",
        "id_pais",
    )
    search_fields = (
        "psicologo__nombres",
        "psicologo__dni",
        "paciente__nombres",
        "paciente__dni",
        "telefono",
        "domicilio",
    )
    list_select_related = (
        "psicologo",
        "paciente",
        "id_sexo",
        "id_std_civil",
        "id_localidad",
        "id_provincia",
        "id_pais",
        "id_zona",
    )
    autocomplete_fields = (
        "psicologo",
        "paciente",
        "id_sexo",
        "id_std_civil",
        "id_pais",
        "id_provincia",
        "id_localidad",
        "id_zona",
    )

    @admin.display(description="Persona")
    def persona_display(self, obj):
        return obj.persona
