from django import forms
from django.contrib.auth.forms import AuthenticationForm


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="",
        widget=forms.TextInput(
            attrs={
                "class": "login-input",
                "placeholder": "Your username",
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="",
        widget=forms.PasswordInput(
            attrs={
                "class": "login-input",
                "placeholder": "Password",
                "autocomplete": "current-password",
            }
        ),
    )
    remember_me = forms.BooleanField(required=False, label="Remember Me")
