from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import TemplateView

from .forms import LoginForm
from .auth_utils import get_panel_role_for_user


class StyledLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = False

    def get_success_url(self):
        user = self.request.user
        panel_role = get_panel_role_for_user(user)

        if panel_role == "admin":
            return reverse_lazy("panel_admin")
        if panel_role == "psicologo":
            return reverse_lazy("panel_psicologo")
        if panel_role == "paciente":
            return reverse_lazy("panel_paciente")
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
        return get_panel_role_for_user(self.request.user) == "admin"


class PanelPsicologoView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "psicologo/panel_psicologo.html"

    def test_func(self):
        return get_panel_role_for_user(self.request.user) == "psicologo"


class PanelPacienteView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "paciente/panel_paciente.html"

    def test_func(self):
        return get_panel_role_for_user(self.request.user) == "paciente"
