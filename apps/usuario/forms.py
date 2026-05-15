from datetime import date
import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from apps.parametro.models import (
    Estado,
    GradoEstudio,
    Localidad,
    Ocupacion,
    Pais,
    Provincia,
    Rama,
    Sexo,
    TipoCivil,
    Zona,
)
from apps.parametro.models.idioma import Idioma
from apps.parametro.models.metodo_pago import MetodoPago

from .models import (
    MAX_SIZE_MB,
    Paciente,
    Psicologo,
    PsicologoIdioma,
    PsicologoMetodoPago,
    PsicologoOficina,
    PsicologoPendiente,
    PsicologoRama,
)


USUARIO_BASE_FIELDS = ["nombres", "email", "dni", "cuil", "fch_nacimiento", "foto"]


def get_estado_activo():
    return Estado.objects.filter(dsc_estado__iexact="ACTIVO", flg_activo=True).first()


class DatosPersonalesSolicitudForm(forms.Form):
    telefono = forms.CharField(max_length=25, widget=forms.TextInput(attrs={"class": "app-input", "placeholder": "Telefono o celular"}))
    domicilio = forms.CharField(max_length=200, widget=forms.TextInput(attrs={"class": "app-input", "placeholder": "Domicilio"}))
    id_sexo = forms.ModelChoiceField(queryset=Sexo.objects.none(), label="Sexo", widget=forms.Select(attrs={"class": "app-select"}))
    id_std_civil = forms.ModelChoiceField(queryset=TipoCivil.objects.none(), label="Estado civil", widget=forms.Select(attrs={"class": "app-select"}))
    id_pais = forms.ModelChoiceField(queryset=Pais.objects.none(), label="Pais", widget=forms.Select(attrs={"class": "app-select"}))
    id_provincia = forms.ModelChoiceField(queryset=Provincia.objects.none(), label="Provincia", widget=forms.Select(attrs={"class": "app-select"}))
    id_localidad = forms.ModelChoiceField(queryset=Localidad.objects.none(), label="Localidad", widget=forms.Select(attrs={"class": "app-select"}))
    id_zona = forms.ModelChoiceField(queryset=Zona.objects.none(), label="Zona", widget=forms.Select(attrs={"class": "app-select"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["id_sexo"].queryset = Sexo.objects.filter(flg_activo=True).order_by("dsc_tipo")
        self.fields["id_std_civil"].queryset = TipoCivil.objects.filter(flg_activo=True).order_by("dsc_std_civil")
        self.fields["id_pais"].queryset = Pais.objects.filter(flg_activo=True).order_by("dsc_pais")
        self.fields["id_provincia"].queryset = Provincia.objects.filter(flg_activo=True).order_by("dsc_provincia")
        self.fields["id_localidad"].queryset = Localidad.objects.filter(flg_activo=True).order_by("dsc_localidad")
        self.fields["id_zona"].queryset = Zona.objects.filter(flg_activo=True).order_by("dsc_zona")


class UsuarioBaseForm(forms.ModelForm):
    password1 = forms.CharField(label="Contrasena", widget=forms.PasswordInput(attrs={"class": "app-input", "placeholder": "Ingresa una contrasena", "autocomplete": "new-password"}))
    password2 = forms.CharField(label="Confirmar contrasena", widget=forms.PasswordInput(attrs={"class": "app-input", "placeholder": "Repite la contrasena", "autocomplete": "new-password"}))

    class Meta:
        fields = USUARIO_BASE_FIELDS
        widgets = {
            "nombres": forms.TextInput(attrs={"class": "app-input", "placeholder": "Nombre completo"}),
            "email": forms.EmailInput(attrs={"class": "app-input", "placeholder": "Correo electronico"}),
            "dni": forms.NumberInput(attrs={"class": "app-input", "placeholder": "DNI"}),
            "cuil": forms.TextInput(attrs={"class": "app-input", "placeholder": "CUIL sin guiones"}),
            "fch_nacimiento": forms.DateInput(attrs={"class": "app-input", "type": "date"}),
            "foto": forms.ClearableFileInput(attrs={"class": "app-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = str(self.instance.dni) if self.instance and self.instance.pk and self.instance.dni else None
        is_editing = bool(self.instance and self.instance.pk)
        self.fields["password1"].required = not is_editing
        self.fields["password2"].required = not is_editing
        if is_editing:
            help_text = "Deja estos campos vacios si no queres cambiar la contrasena."
            self.fields["password1"].help_text = help_text
            self.fields["password2"].help_text = help_text
        self.fields["foto"].required = False
        self.fields["foto"].help_text = f"La foto es opcional: podes dejarla vacia. Si cargas una imagen, usa JPG, PNG o WEBP de hasta {MAX_SIZE_MB} MB."

    @staticmethod
    def get_default_estado():
        return get_estado_activo()

    def save(self, commit=True):
        usuario = super().save(commit=False)
        if hasattr(usuario, "id_estado_id") and (not usuario.pk or not usuario.id_estado_id):
            usuario.id_estado = self.get_default_estado()
        if commit:
            usuario.save()
            self.save_m2m()
        return usuario

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

    def save_auth_user(self, usuario):
        password = self.cleaned_data.get("password1")
        username = str(usuario.dni)
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
        user.email = usuario.email
        if hasattr(user, "first_name"):
            user.first_name = usuario.nombres[:150]
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()
        user.save()
        return user


class PsicologoForm(UsuarioBaseForm):
    ramas = forms.ModelMultipleChoiceField(
        queryset=Rama.objects.none(),
        label="Ramas",
        widget=forms.CheckboxSelectMultiple,
        help_text="Marca todas las ramas en las que querés ofrecer atención profesional.",
    )

    class Meta(UsuarioBaseForm.Meta):
        model = Psicologo
        fields = USUARIO_BASE_FIELDS + ["titulo"]
        widgets = {
            **UsuarioBaseForm.Meta.widgets,
            "titulo": forms.ClearableFileInput(
                attrs={"class": "app-input", "accept": "application/pdf,.pdf"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["ramas"].queryset = Rama.objects.filter(
            flg_activo=True
        ).order_by("dsc_rama")

        if self.instance and self.instance.pk:
            self.fields["ramas"].initial = list(
                self.instance.ramas.filter(
                    id_estado__dsc_estado__iexact="ACTIVO",
                    id_estado__flg_activo=True,
                ).values_list("id_rama_id", flat=True)
            )

        self.fields["titulo"].label = "Titulo"
        self.fields["titulo"].help_text = (
            "Adjunta el titulo profesional en formato PDF. "
            "Es obligatorio para enviar la solicitud."
        )

    def clean_ramas(self):
        ramas = self.cleaned_data.get("ramas")

        if not ramas:
            raise ValidationError("Debés seleccionar al menos una rama.")

        return ramas

    def sync_ramas(self, psicologo):
        estado_activo = get_estado_activo()
        estado_inactivo = Estado.objects.filter(
            dsc_estado__iexact="INACTIVO",
            flg_activo=True,
        ).first()

        if estado_activo is None:
            raise ValidationError("No hay un estado ACTIVO configurado.")

        if estado_inactivo is None:
            raise ValidationError("No hay un estado INACTIVO configurado.")

        ramas_seleccionadas = set(
            self.cleaned_data["ramas"].values_list("pk", flat=True)
        )

        relaciones = {
            relacion.id_rama_id: relacion
            for relacion in PsicologoRama.objects.filter(
                id_psicologo=psicologo
            ).select_related("id_estado", "id_rama")
        }

        for rama_id in ramas_seleccionadas:
            relacion = relaciones.get(rama_id)

            if relacion is None:
                PsicologoRama.objects.create(
                    id_psicologo=psicologo,
                    id_rama_id=rama_id,
                    valor_sesion=0,
                    id_estado=estado_activo,
                )
                continue

            if relacion.id_estado_id != estado_activo.pk:
                relacion.id_estado = estado_activo
                relacion.valor_sesion = 0
                relacion.save(update_fields=["id_estado", "valor_sesion"])

        for rama_id, relacion in relaciones.items():
            if rama_id not in ramas_seleccionadas and relacion.id_estado_id != estado_inactivo.pk:
                relacion.id_estado = estado_inactivo
                relacion.valor_sesion = 0
                relacion.save(update_fields=["id_estado", "valor_sesion"])

        if hasattr(psicologo, "ramas_activas"):
            delattr(psicologo, "ramas_activas")

    def save(self, commit=True):
        psicologo = super().save(commit=False)

        if commit:
            psicologo.save()
            self.sync_ramas(psicologo)
            self.save_m2m()

        return psicologo


class PsicologoPendienteForm(UsuarioBaseForm):
    ramas = forms.ModelMultipleChoiceField(
        queryset=Rama.objects.none(),
        label="Ramas",
        widget=forms.CheckboxSelectMultiple,
        help_text="Marca todas las ramas en las que quieres ofrecer atencion profesional.",
    )

    class Meta(UsuarioBaseForm.Meta):
        model = PsicologoPendiente
        fields = USUARIO_BASE_FIELDS + ["titulo"]
        widgets = {
            **UsuarioBaseForm.Meta.widgets,
            "titulo": forms.ClearableFileInput(
                attrs={"class": "app-input", "accept": "application/pdf,.pdf"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ramas"].queryset = Rama.objects.filter(flg_activo=True).order_by("dsc_rama")
        if self.instance and self.instance.pk:
            self.fields["ramas"].initial = [
                rama.pk for rama in self.instance.get_ramas_pendientes()
            ]
        self.fields["titulo"].label = "Titulo"
        self.fields["titulo"].help_text = "Adjunta el titulo profesional en formato PDF. Es obligatorio para enviar la solicitud."

    @staticmethod
    def get_active_solicitudes():
        return PsicologoPendiente.objects.exclude(estado=PsicologoPendiente.ESTADO_RECHAZADO)

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if Psicologo.objects.filter(email__iexact=email).exists():
            raise ValidationError("Ya existe un psicologo aprobado con este correo electronico.")
        if self.get_active_solicitudes().filter(email__iexact=email).exists():
            raise ValidationError("Ya existe una solicitud pendiente o aprobada con este correo electronico.")
        return email

    def clean_dni(self):
        dni = self.cleaned_data.get("dni")
        if dni and not re.match(r"^\d{7,8}$", str(dni)):
            raise ValidationError("El DNI debe tener 7 u 8 digitos.")
        if dni and Psicologo.objects.filter(dni=dni).exists():
            raise ValidationError("Ya existe un psicologo aprobado con este DNI.")
        if dni and self.get_active_solicitudes().filter(dni=dni).exists():
            raise ValidationError("Ya existe una solicitud pendiente o aprobada con este DNI.")
        username = str(dni) if dni else ""
        if username and get_user_model().objects.filter(username=username).exists():
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
        if Psicologo.objects.filter(cuil=cuil).exists():
            raise ValidationError("Ya existe un psicologo aprobado con este CUIL.")
        if self.get_active_solicitudes().filter(cuil=cuil).exists():
            raise ValidationError("Ya existe una solicitud pendiente o aprobada con este CUIL.")
        return cuil

    def save(self, commit=True):
        solicitud = super().save(commit=False)
        solicitud.password_hash = make_password(self.cleaned_data["password1"])
        solicitud.estado = PsicologoPendiente.ESTADO_PENDIENTE
        solicitud.set_ramas_pendientes(self.cleaned_data.get("ramas"))
        if commit:
            solicitud.save()
        return solicitud


class PacienteForm(UsuarioBaseForm):
    class Meta(UsuarioBaseForm.Meta):
        model = Paciente
        fields = USUARIO_BASE_FIELDS + ["id_ocupacion", "id_grado_estudio"]
        widgets = {**UsuarioBaseForm.Meta.widgets, "id_ocupacion": forms.Select(attrs={"class": "app-select"}), "id_grado_estudio": forms.Select(attrs={"class": "app-select"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fch_nacimiento"].help_text = "Con esta fecha el sistema calcula automaticamente el ciclo de vida."
        self.fields["id_ocupacion"].queryset = Ocupacion.objects.filter(flg_activo=True).order_by("dsc_ocupacion")
        self.fields["id_grado_estudio"].queryset = GradoEstudio.objects.filter(flg_activo=True).order_by("dsc_grado_estudio")


class PsicologoOficinaForm(forms.ModelForm):
    class Meta:
        model = PsicologoOficina
        fields = ["id_psicologo", "domicilio", "telefono", "id_pais", "id_provincia", "id_localidad", "id_zona", "id_estado"]
        widgets = {
            "id_psicologo": forms.Select(attrs={"class": "app-select"}),
            "domicilio": forms.TextInput(attrs={"class": "app-input", "placeholder": "Domicilio de la oficina"}),
            "telefono": forms.TextInput(attrs={"class": "app-input", "placeholder": "Telefono de contacto"}),
            "id_pais": forms.Select(attrs={"class": "app-select"}),
            "id_provincia": forms.Select(attrs={"class": "app-select"}),
            "id_localidad": forms.Select(attrs={"class": "app-select"}),
            "id_zona": forms.Select(attrs={"class": "app-select"}),
            "id_estado": forms.Select(attrs={"class": "app-select"}),
        }

    def __init__(self, *args, user=None, psicologo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.psicologo = psicologo
        self.is_psicologo_user = bool(self.psicologo and not (self.user and (self.user.is_staff or self.user.is_superuser)))
        self.fields["id_psicologo"].queryset = Psicologo.objects.order_by("nombres", "dni")
        self.fields["id_pais"].queryset = Pais.objects.filter(flg_activo=True).order_by("dsc_pais")
        self.fields["id_provincia"].queryset = Provincia.objects.filter(flg_activo=True).order_by("dsc_provincia")
        self.fields["id_localidad"].queryset = Localidad.objects.filter(flg_activo=True).order_by("dsc_localidad")
        self.fields["id_zona"].queryset = Zona.objects.filter(flg_activo=True).order_by("dsc_zona")
        self.fields["id_estado"].queryset = Estado.objects.filter(flg_activo=True).order_by("dsc_estado")

        if self.instance and self.instance.pk and self.instance.id_psicologo_id:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(
                pk=self.instance.id_psicologo_id
            )
            self.fields["id_psicologo"].initial = self.instance.id_psicologo
            self.fields["id_psicologo"].disabled = True

        elif self.is_psicologo_user:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(
                pk=self.psicologo.pk
            )
            self.fields["id_psicologo"].initial = self.psicologo
            self.fields["id_psicologo"].disabled = True
            self.fields["id_estado"].required = False
            self.fields["id_estado"].widget = forms.HiddenInput()
            self.fields["id_estado"].initial = get_estado_activo()

    def save(self, commit=True):
        oficina = super().save(commit=False)
        if self.fields["id_psicologo"].disabled:
            if self.instance and self.instance.pk:
                oficina.id_psicologo = self.instance.id_psicologo
            elif self.psicologo:
                oficina.id_psicologo = self.psicologo
        if self.is_psicologo_user:
            oficina.id_estado = get_estado_activo()
        if commit:
            oficina.save()
            self.save_m2m()
        return oficina


class PsicologoMetodoPagoForm(forms.ModelForm):
    class Meta:
        model = PsicologoMetodoPago
        fields = ["id_psicologo", "id_metodo_pago", "id_estado"]
        widgets = {"id_psicologo": forms.Select(attrs={"class": "app-select"}), "id_metodo_pago": forms.Select(attrs={"class": "app-select"}), "id_estado": forms.Select(attrs={"class": "app-select"})}

    def __init__(self, *args, user=None, psicologo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.psicologo = psicologo
        self.is_psicologo_user = bool(self.psicologo and not (self.user and (self.user.is_staff or self.user.is_superuser)))
        self.fields["id_psicologo"].queryset = Psicologo.objects.order_by("nombres", "dni")
        self.fields["id_metodo_pago"].queryset = MetodoPago.objects.filter(flg_activo=True).order_by("dsc_met_pago")
        self.fields["id_estado"].queryset = Estado.objects.filter(flg_activo=True).order_by("dsc_estado")

        if self.instance and self.instance.pk and self.instance.id_psicologo_id:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(pk=self.instance.id_psicologo_id)
            self.fields["id_psicologo"].initial = self.instance.id_psicologo
            self.fields["id_psicologo"].disabled = True
        elif self.is_psicologo_user:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(pk=self.psicologo.pk)
            self.fields["id_psicologo"].initial = self.psicologo
            self.fields["id_psicologo"].disabled = True
            self.fields["id_estado"].required = False
            self.fields["id_estado"].widget = forms.HiddenInput()
            self.fields["id_estado"].initial = get_estado_activo()

    def clean(self):
        cleaned_data = super().clean()
        psicologo = self.instance.id_psicologo if self.instance and self.instance.pk and self.fields["id_psicologo"].disabled else (self.psicologo if self.fields["id_psicologo"].disabled else cleaned_data.get("id_psicologo"))
        metodo_pago = cleaned_data.get("id_metodo_pago")
        if psicologo and metodo_pago:
            queryset = PsicologoMetodoPago.objects.filter(id_psicologo=psicologo, id_metodo_pago=metodo_pago)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Este metodo de pago ya esta cargado para el psicologo.")
        return cleaned_data

    def save(self, commit=True):
        metodo_pago = super().save(commit=False)
        if self.fields["id_psicologo"].disabled:
            if self.instance and self.instance.pk:
                metodo_pago.id_psicologo = self.instance.id_psicologo
            elif self.psicologo:
                metodo_pago.id_psicologo = self.psicologo
        if self.is_psicologo_user:
            metodo_pago.id_estado = get_estado_activo()
        if commit:
            metodo_pago.save()
            self.save_m2m()
        return metodo_pago


class PsicologoRamaForm(forms.ModelForm):
    class Meta:
        model = PsicologoRama
        fields = ["id_psicologo", "id_rama", "valor_sesion", "id_estado"]
        widgets = {
            "id_psicologo": forms.Select(attrs={"class": "app-select"}),
            "id_rama": forms.Select(attrs={"class": "app-select"}),
            "valor_sesion": forms.NumberInput(
                attrs={
                    "class": "app-input",
                    "placeholder": "Valor por sesion",
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "id_estado": forms.Select(attrs={"class": "app-select"}),
        }

    def __init__(self, *args, user=None, psicologo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.psicologo = psicologo
        self.is_psicologo_user = bool(
            self.psicologo and not (self.user and (self.user.is_staff or self.user.is_superuser))
        )

        self.fields["id_psicologo"].queryset = Psicologo.objects.order_by("nombres", "dni")
        self.fields["id_rama"].queryset = Rama.objects.filter(flg_activo=True).order_by("dsc_rama")
        self.fields["id_estado"].queryset = Estado.objects.filter(flg_activo=True).order_by("dsc_estado")
        self.fields["valor_sesion"].required = False
        self.fields["valor_sesion"].initial = self.fields["valor_sesion"].initial or 0
        self.fields["valor_sesion"].help_text = "Puedes dejarlo en 0 si todavia no quieres definir un valor."

        if self.instance and self.instance.pk and self.instance.id_psicologo_id:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(
                pk=self.instance.id_psicologo_id
            )
            self.fields["id_psicologo"].initial = self.instance.id_psicologo
            self.fields["id_psicologo"].disabled = True
        elif self.is_psicologo_user:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(pk=self.psicologo.pk)
            self.fields["id_psicologo"].initial = self.psicologo
            self.fields["id_psicologo"].disabled = True
            self.fields["id_estado"].required = False
            self.fields["id_estado"].widget = forms.HiddenInput()
            self.fields["id_estado"].initial = get_estado_activo()

    def clean(self):
        cleaned_data = super().clean()
        if self.instance and self.instance.pk and self.fields["id_psicologo"].disabled:
            psicologo = self.instance.id_psicologo
        elif self.fields["id_psicologo"].disabled:
            psicologo = self.psicologo
        else:
            psicologo = cleaned_data.get("id_psicologo")

        rama = cleaned_data.get("id_rama")

        if psicologo and rama:
            queryset = PsicologoRama.objects.filter(id_psicologo=psicologo, id_rama=rama)
            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)
            if queryset.exists():
                raise ValidationError("Esta rama ya esta cargada para el psicologo.")

        return cleaned_data

    def save(self, commit=True):
        psicologo_rama = super().save(commit=False)
        if self.fields["id_psicologo"].disabled:
            if self.instance and self.instance.pk:
                psicologo_rama.id_psicologo = self.instance.id_psicologo
            elif self.psicologo:
                psicologo_rama.id_psicologo = self.psicologo
        if self.is_psicologo_user:
            psicologo_rama.id_estado = get_estado_activo()
        if commit:
            psicologo_rama.save()
            self.save_m2m()
        return psicologo_rama


class PsicologoIdiomaForm(forms.ModelForm):
    class Meta:
        model = PsicologoIdioma
        fields = ["id_psicologo", "id_idioma", "id_estado"]
        widgets = {
            "id_psicologo": forms.Select(attrs={"class": "app-select"}),
            "id_idioma": forms.Select(attrs={"class": "app-select"}),
            "id_estado": forms.Select(attrs={"class": "app-select"}),
        }

    def __init__(self, *args, user=None, psicologo=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.psicologo = psicologo
        self.is_psicologo_user = bool(
            self.psicologo and not (
                self.user and (self.user.is_staff or self.user.is_superuser)
            )
        )

        self.fields["id_psicologo"].queryset = Psicologo.objects.order_by("nombres", "dni")
        self.fields["id_idioma"].queryset = Idioma.objects.filter(
            flg_activo=True
        ).order_by("dsc_idioma")
        self.fields["id_estado"].queryset = Estado.objects.filter(
            flg_activo=True
        ).order_by("dsc_estado")

        if self.instance and self.instance.pk and self.instance.id_psicologo_id:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(
                pk=self.instance.id_psicologo_id
            )
            self.fields["id_psicologo"].initial = self.instance.id_psicologo
            self.fields["id_psicologo"].disabled = True

        elif self.is_psicologo_user:
            self.fields["id_psicologo"].queryset = Psicologo.objects.filter(
                pk=self.psicologo.pk
            )
            self.fields["id_psicologo"].initial = self.psicologo
            self.fields["id_psicologo"].disabled = True
            self.fields["id_estado"].required = False
            self.fields["id_estado"].widget = forms.HiddenInput()
            self.fields["id_estado"].initial = get_estado_activo()

    def clean(self):
        cleaned_data = super().clean()

        if self.instance and self.instance.pk and self.fields["id_psicologo"].disabled:
            psicologo = self.instance.id_psicologo
        elif self.fields["id_psicologo"].disabled:
            psicologo = self.psicologo
        else:
            psicologo = cleaned_data.get("id_psicologo")

        idioma = cleaned_data.get("id_idioma")

        if psicologo and idioma:
            queryset = PsicologoIdioma.objects.filter(
                id_psicologo=psicologo,
                id_idioma=idioma,
            )

            if self.instance.pk:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError("Este idioma ya esta cargado para el psicologo.")

        return cleaned_data

    def save(self, commit=True):
        idioma = super().save(commit=False)

        if self.fields["id_psicologo"].disabled:
            if self.instance and self.instance.pk:
                idioma.id_psicologo = self.instance.id_psicologo
            elif self.psicologo:
                idioma.id_psicologo = self.psicologo

        if self.is_psicologo_user:
            idioma.id_estado = get_estado_activo()

        if commit:
            idioma.save()
            self.save_m2m()

        return idioma
