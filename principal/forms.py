from django import forms
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .auth_utils import user_has_inactive_profile


class LoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "inactive_profile": (
            "Tu cuenta esta inactiva. Comunicate con administracion para volver a habilitarla."
        ),
    }

    username = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "login-input",
                "placeholder": "Ingresa tu DNI",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "login-input",
                "placeholder": "Ingresa tu contraseña",
                "autocomplete": "current-password",
            }
        ),
    )
    remember_me = forms.BooleanField(required=False, label="Recordarme")

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if username and password:
            self.user_cache = authenticate(
                self.request,
                username=username,
                password=password,
            )
            if self.user_cache is None:
                user_model = get_user_model()
                raw_user = user_model._default_manager.filter(
                    **{user_model.USERNAME_FIELD: username}
                ).first()
                if raw_user and raw_user.check_password(password) and user_has_inactive_profile(
                    raw_user
                ):
                    raise ValidationError(
                        self.error_messages["inactive_profile"],
                        code="inactive_profile",
                    )
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data
