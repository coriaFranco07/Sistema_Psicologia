from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from apps.usuario.models import Psicologo

from .forms import LoginForm


class StyledLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return reverse_lazy("panel_admin")
        if Psicologo.objects.filter(dni=user.username).exists():
            return reverse_lazy("panel_psicologo")
        return super().get_success_url()

    def form_valid(self, form):
        response = super().form_valid(form)
        if form.cleaned_data.get("remember_me"):
            self.request.session.set_expiry(60 * 60 * 24 * 30)
        else:
            self.request.session.set_expiry(0)
        return response


class PanelAdminView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "panel_admin.html"

    def test_func(self):
        user = self.request.user
        return user.is_staff or user.is_superuser


class PanelPsicologoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "psicologo/panel_psicologo.html"

    def test_func(self):
        return Psicologo.objects.filter(dni=self.request.user.username).exists()
