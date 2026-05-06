from django import forms

from apps.parametro.models import Localidad, Pais, Provincia, Sexo, TipoCivil, Zona

from .models import DatosPersonales


class DatosPersonalesForm(forms.ModelForm):
    class Meta:
        model = DatosPersonales
        fields = [
            "telefono",
            "domicilio",
            "id_sexo",
            "id_std_civil",
            "id_pais",
            "id_provincia",
            "id_localidad",
            "id_zona",
        ]
        widgets = {
            "telefono": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Telefono o celular"}
            ),
            "domicilio": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Domicilio"}
            ),
            "id_sexo": forms.Select(attrs={"class": "app-select"}),
            "id_std_civil": forms.Select(attrs={"class": "app-select"}),
            "id_pais": forms.Select(attrs={"class": "app-select"}),
            "id_provincia": forms.Select(attrs={"class": "app-select"}),
            "id_localidad": forms.Select(attrs={"class": "app-select"}),
            "id_zona": forms.Select(attrs={"class": "app-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_sexo"].queryset = Sexo.objects.filter(flg_activo=True).order_by("dsc_tipo")
        self.fields["id_std_civil"].queryset = TipoCivil.objects.filter(flg_activo=True).order_by(
            "dsc_std_civil"
        )
        self.fields["id_pais"].queryset = Pais.objects.filter(flg_activo=True).order_by("dsc_pais")
        self.fields["id_provincia"].queryset = Provincia.objects.filter(flg_activo=True).order_by(
            "dsc_provincia"
        )
        self.fields["id_localidad"].queryset = Localidad.objects.filter(flg_activo=True).order_by(
            "dsc_localidad"
        )
        self.fields["id_zona"].queryset = Zona.objects.filter(flg_activo=True).order_by("dsc_zona")
