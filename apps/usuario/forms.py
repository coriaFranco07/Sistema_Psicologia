from datetime import date
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.parametro.models import CicloVida, Estado, GradoEstudio, Ocupacion

from .models import MAX_SIZE_MB, Paciente, Psicologo


PERSONA_FIELDS = ["nombres", "email", "dni", "cuil", "fch_nacimiento", "foto"]


class BasePersonaForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contrasena",
        widget=forms.PasswordInput(
            attrs={
                "class": "app-input",
                "placeholder": "Ingresa una contrasena",
                "autocomplete": "new-password",
            }
        ),
    )
    password2 = forms.CharField(
        label="Confirmar contrasena",
        widget=forms.PasswordInput(
            attrs={
                "class": "app-input",
                "placeholder": "Repite la contrasena",
                "autocomplete": "new-password",
            }
        ),
    )

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
            "foto": forms.ClearableFileInput(attrs={"class": "app-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = (
            str(self.instance.dni) if self.instance and self.instance.pk and self.instance.dni else None
        )
        is_editing = bool(self.instance and self.instance.pk)
        self.fields["password1"].required = not is_editing
        self.fields["password2"].required = not is_editing
        if is_editing:
            help_text = "Deja estos campos vacios si no queres cambiar la contrasena."
            self.fields["password1"].help_text = help_text
            self.fields["password2"].help_text = help_text

        self.fields["foto"].required = False
        self.fields["foto"].help_text = (
            f"La foto es opcional: podes dejarla vacia. Si cargas una imagen, usa JPG, PNG o WEBP de hasta {MAX_SIZE_MB} MB."
        )

    @staticmethod
    def get_default_estado():
        return Estado.objects.filter(dsc_estado__iexact="ACTIVO", flg_activo=True).first()

    def save(self, commit=True):
        persona = super().save(commit=False)
        if not persona.pk or not persona.id_estado_id:
            persona.id_estado = self.get_default_estado()

        if commit:
            persona.save()
            self.save_m2m()

        return persona

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

        username = str(dni) if dni else ""
        if username:
            user_exists = get_user_model().objects.filter(username=username).exists()
            if user_exists and username != self.original_username:
                raise ValidationError("Ya existe un usuario de acceso con este DNI.")

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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 or password2:
            if password1 != password2:
                self.add_error("password2", "Las contrasenas no coinciden.")
            else:
                try:
                    validate_password(password1)
                except ValidationError as error:
                    self.add_error("password1", error)

        if not self.instance.pk and self.get_default_estado() is None:
            raise ValidationError("No hay un estado ACTIVO configurado para crear el registro.")

        return cleaned_data

    def save_auth_user(self, persona):
        password = self.cleaned_data.get("password1")
        username = str(persona.dni)
        UserModel = get_user_model()
        user = None

        if self.original_username:
            user = UserModel.objects.filter(username=self.original_username).first()

        if user is None:
            user = UserModel.objects.filter(username=username).first()

        if user is None:
            if not password and self.instance.pk:
                return None
            user = UserModel(username=username)

        user.username = username
        user.email = persona.email
        if hasattr(user, "first_name"):
            user.first_name = persona.nombres[:150]

        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()

        user.save()
        return user


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
