import logging
from django import forms

from apps.core.utils import log_error
from .models import PermisoModulo, Modulo
from apps.usuario.models import Usuario

logger = logging.getLogger(__name__)

class ModuloForm(forms.ModelForm):
    class Meta:
        model = Modulo
        fields = ['nombre', 'descripcion', 'codigo', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        try:
            qs = Modulo.objects.filter(nombre__iexact=nombre)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un módulo con este nombre.")
        except Exception as e:
            logger.exception(f"Error validando nombre de módulo: {nombre} -> {str(e)}")
            log_error(
                mensaje=f"Error validando nombre de módulo: {nombre} -> {str(e)}"
            )
            raise forms.ValidationError("Error validando nombre de módulo.")
        return nombre

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        try:
            qs = Modulo.objects.filter(codigo__iexact=codigo)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("Ya existe un módulo con este código.")
        except Exception as e:
            logger.exception(f"Error validando código de módulo: {codigo} -> {str(e)}")
            log_error(
                mensaje=f"Error validando codigo de módulo: {codigo} -> {str(e)}"
            )
            raise forms.ValidationError("Error validando código de módulo.")
        return codigo


class PermisoModuloForm(forms.ModelForm):
    class Meta:
        model = PermisoModulo
        fields = ['usuario', 'modulo', 'puede_ver', 'puede_editar', 'puede_eliminar','puede_agregar']
        widgets = {
            'usuario': forms.Select(attrs={'class': 'form-select select2'}),
            'modulo': forms.Select(attrs={'class': 'form-select select2'}),
            'puede_ver': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_editar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_eliminar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_agregar': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            # Opcional: filtrar usuarios que no son admin_local ni staff
            self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True)\
                .exclude(es_admin_local=True).exclude(is_staff=True)
        except Exception as e:
            logger.exception(f"Error cargando queryset de usuarios: {str(e)}")
            log_error(
                mensaje=f"Error cargando queryset de usuarios: {str(e)}"
            )
            self.fields['usuario'].queryset = Usuario.objects.filter(is_active=True)
