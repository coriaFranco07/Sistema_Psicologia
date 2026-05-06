from datetime import date
import re

from django import forms
from django.core.exceptions import ValidationError

from apps.parametro.models import CicloVida, Estado, GradoEstudio, Ocupacion

from .models import MAX_SIZE_MB, Paciente, Psicologo


PERSONA_FIELDS = ["nombres", "email", "dni", "cuil", "fch_nacimiento", "id_estado", "foto"]


class BasePersonaForm(forms.ModelForm):
    class Meta:
        fields = PERSONA_FIELDS
        widgets = {
            "nombres": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "Nombre completo"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "app-input", "placeholder": "Correo electronico"}
            ),
            "dni": forms.NumberInput(attrs={"class": "app-input", "placeholder": "DNI"}),
            "cuil": forms.TextInput(
                attrs={"class": "app-input", "placeholder": "CUIL sin guiones"}
            ),
            "fch_nacimiento": forms.DateInput(
                attrs={"class": "app-input", "type": "date"}
            ),
            "id_estado": forms.Select(attrs={"class": "app-select"}),
            "foto": forms.ClearableFileInput(attrs={"class": "app-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_estado"].queryset = Estado.objects.filter(flg_activo=True).order_by(
            "dsc_estado"
        )
        self.fields["foto"].required = False
        self.fields["foto"].help_text = (
            f"Subi una imagen JPG, PNG o WEBP de hasta {MAX_SIZE_MB} MB."
        )

    def clean_nombres(self):
        nombres = self.cleaned_data.get("nombres", "").strip()
        if not nombres:
            raise ValidationError("El nombre es obligatorio.")
        return nombres

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        model = self._meta.model
        queryset = model.objects.filter(email__iexact=email)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe un registro con este correo electronico.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if dni and not re.match(r"^\d{7,8}$", str(dni)):
            raise ValidationError("El DNI debe tener 7 u 8 digitos.")

        model = self._meta.model
        queryset = model.objects.filter(dni=dni)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if dni and queryset.exists():
            raise ValidationError("Ya existe un registro con este DNI.")
        return dni

    def clean_cuil(self):
        cuil = self.cleaned_data.get("cuil")
        dni = self.cleaned_data.get("dni")

        if not cuil:
            return cuil

        cuil = str(cuil).strip()
        if not re.match(r"^\d{11}$", cuil):
            raise ValidationError("El CUIL debe tener 11 digitos sin guiones.")

        if dni and cuil[2:10] != str(dni).zfill(8):
            raise ValidationError("Los digitos centrales del CUIL deben coincidir con el DNI.")

        model = self._meta.model
        queryset = model.objects.filter(cuil=cuil)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise ValidationError("Ya existe un registro con este CUIL.")
        return cuil

    def clean_fch_nacimiento(self):
        fch_nacimiento = self.cleaned_data.get("fch_nacimiento")
        if fch_nacimiento and fch_nacimiento > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser posterior a hoy.")
        return fch_nacimiento


class PsicologoForm(BasePersonaForm):
    class Meta(BasePersonaForm.Meta):
        model = Psicologo


class PacienteForm(BasePersonaForm):
    class Meta(BasePersonaForm.Meta):
        model = Paciente
        fields = PERSONA_FIELDS + ["id_ocupacion", "id_ciclo_vida", "id_grado_estudio"]
        widgets = {
            **BasePersonaForm.Meta.widgets,
            "id_ocupacion": forms.Select(attrs={"class": "app-select"}),
            "id_ciclo_vida": forms.Select(attrs={"class": "app-select"}),
            "id_grado_estudio": forms.Select(attrs={"class": "app-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_ocupacion"].queryset = Ocupacion.objects.filter(flg_activo=True).order_by(
            "dsc_ocupacion"
        )
        self.fields["id_ciclo_vida"].queryset = CicloVida.objects.filter(flg_activo=True).order_by(
            "dsc_ciclo_vida"
        )
        self.fields["id_grado_estudio"].queryset = GradoEstudio.objects.filter(
            flg_activo=True
        ).order_by("dsc_grado_estudio")
