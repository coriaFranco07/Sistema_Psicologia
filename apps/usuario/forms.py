from datetime import date
from django import forms
from .models import Usuario
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()
import re
from django.core.exceptions import ValidationError

class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Contraseña",
            "id": "password1"
        })
    )

    password2 = forms.CharField(
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirmar contraseña",
            "id": "password2"
        })
    )

    class Meta:
        model = Usuario
        fields = ["username", "dni", "cuil", "email", "nombres", "fch_nacimiento", "id_tipo_socio", "id_jerarquia"]
        widgets = {
            "username": forms.HiddenInput(),
            "dni": forms.NumberInput(attrs={"class": "form-control", "placeholder": "DNI"}),
            "cuil": forms.TextInput(attrs={"class": "form-control", "placeholder": "CUIL SIN GUIONES"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "fch_nacimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "id": "fch_nacimiento",
                    "placeholder": "Año/Mes/Día",
                }
            ),
            "id_tipo_socio": forms.Select(attrs={"class": "form-select"}),
            "id_jerarquia": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = False



    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if dni:
            if not re.match(r"^\d{7,8}$", str(dni)):
                raise ValidationError("DNI inválido. Debe tener 7 u 8 dígitos.")
            
            # Verificar si ya existe un usuario con ese DNI como username
            if Usuario.objects.filter(username=str(dni)).exists():
                raise ValidationError("Ya existe un usuario con este DNI.")
        return dni
    
    def clean_cuil(self):
        cuil = self.cleaned_data.get("cuil")
        dni = self.cleaned_data.get("dni")

        if cuil:
            cuil = str(cuil)

            # Validar que tenga 11 dígitos
            if not re.match(r"^\d{11}$", cuil):
                raise ValidationError("CUIL inválido. Debe tener 11 dígitos sin guiones.")

            # Extraer los 8 del medio
            cuil_dni = cuil[2:10]

            if dni:
                dni_padded = str(dni).zfill(8)

                if cuil_dni != dni_padded:
                    raise ValidationError(
                        "Los dígitos centrales del CUIL deben coincidir con el DNI ingresado."
                    )

        return cuil
    
    def clean_fch_nacimiento(self):
        fch_nacimiento = self.cleaned_data.get("fch_nacimiento")
        if fch_nacimiento and fch_nacimiento > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser posterior a hoy.")
        return fch_nacimiento

    def clean(self):
        cleaned_data = super().clean()

        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")

        # Asignar automáticamente el username con el DNI
        dni = cleaned_data.get("dni")
        if dni:
            cleaned_data["username"] = str(dni)


        return cleaned_data
    
class UsuarioUpdateForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ["username", "dni", "cuil", "email", "nombres", "fch_nacimiento", "id_tipo_socio", "id_jerarquia"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre de usuario"}),
            "dni": forms.NumberInput(attrs={"class": "form-control", "placeholder": "DNI"}),
            "cuil": forms.TextInput(attrs={"class": "form-control", "placeholder": "CUIL SIN GUIONES"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "Correo electrónico"}),
            "nombres": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo"}),
            "fch_nacimiento": forms.DateInput(
                attrs={
                    "class": "form-control",
                    "id": "fch_nacimiento",
                    "placeholder": "Año/Mes/Día",
                }
            ),
            "id_tipo_socio": forms.Select(attrs={"class": "form-select"}),
            "id_jerarquia": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, is_edit=False, **kwargs):
        super().__init__(*args, **kwargs)

        if is_edit:
            # Quitar tipo de socio si es edición
            if "id_tipo_socio" in self.fields:
                del self.fields["id_tipo_socio"]



    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if dni:
            if not re.match(r"^\d{7,8}$", str(dni)):
                raise ValidationError("DNI inválido. Debe tener 7 u 8 dígitos.")
        return dni
    

    def clean_cuil(self):
        cuil = self.cleaned_data.get("cuil")
        dni = self.cleaned_data.get("dni")

        if cuil:
            cuil = str(cuil)  # 👈 convertir a string

            # Validar que tenga 11 dígitos
            if not re.match(r"^\d{11}$", cuil):
                raise ValidationError("CUIL inválido. Debe tener 11 dígitos sin guiones.")

            # Extraer los 8 del medio
            cuil_dni = cuil[2:10]

            if dni:
                dni_padded = str(dni).zfill(8)

                if cuil_dni != dni_padded:
                    raise ValidationError(
                        "Los dígitos centrales del CUIL deben coincidir con el DNI ingresado."
                    )

        return cuil

    def clean_fch_nacimiento(self):
        fch_nacimiento = self.cleaned_data.get("fch_nacimiento")
        if fch_nacimiento and fch_nacimiento > date.today():
            raise ValidationError("La fecha de nacimiento no puede ser posterior a hoy.")
        return fch_nacimiento

