from datetime import date

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.parametro.models import CicloVida, Estado, GradoEstudio, Ocupacion, Rama
from apps.usuario.models import Paciente, Psicologo


class HomePageTests(TestCase):
    def test_home_page_shows_services_and_registration_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "MenteClara")
        self.assertContains(response, reverse("usuario:paciente_create"))
        self.assertContains(response, reverse("usuario:psicologo_create"))


class LoginPageTests(TestCase):
    def test_login_page_shows_form_and_branding(self):
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Iniciar sesion")
        self.assertContains(response, "MenteClara")
        self.assertContains(response, "images/MenteClara_sinFondo.png")


class PanelAdminPageTests(TestCase):
    def test_staff_user_sees_simplified_admin_panel(self):
        user = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="ClaveSegura123",
        )
        user.is_staff = True
        user.save()
        self.client.force_login(user)

        response = self.client.get(reverse("panel_admin"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Gestion r")
        self.assertContains(response, "Accesos principales")
        self.assertContains(response, "Solicitudes pendientes")
        self.assertContains(response, "admin")
        self.assertContains(response, 'class="admin-status-dot"', html=False)
        self.assertContains(response, f'action="{reverse("logout")}"', html=False)
        self.assertContains(response, 'method="post"', html=False)


class PanelPacientePageTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.ocupacion = Ocupacion.objects.create(
            dsc_ocupacion="ESTUDIANTE",
            flg_activo=True,
        )
        self.grado_estudio = GradoEstudio.objects.create(
            dsc_grado_estudio="SECUNDARIO",
            flg_activo=True,
        )
        self.ciclo_vida = CicloVida.objects.create(
            dsc_ciclo_vida="ADULTEZ INICIAL",
            flg_activo=True,
        )
        self.paciente = Paciente.objects.create(
            nombres="Paula Paciente",
            email="paula@example.com",
            dni=33111222,
            cuil=20331112220,
            fch_nacimiento=date(1998, 4, 20),
            id_estado=self.estado_activo,
            id_ocupacion=self.ocupacion,
            id_ciclo_vida=self.ciclo_vida,
            id_grado_estudio=self.grado_estudio,
        )
        self.user = get_user_model().objects.create_user(
            username="33111222",
            email="paula@example.com",
            password="ClaveSegura123",
        )

    def test_patient_user_sees_simple_panel(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("panel_paciente"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Panel paciente")
        self.assertContains(response, "Mi espacio personal")
        self.assertContains(response, "Tu espacio personal, simple y claro.")
        self.assertContains(response, reverse("usuario:paciente_mi_perfil"))
        self.assertContains(response, reverse("usuario:paciente_mis_psicologos"))
        self.assertContains(response, reverse("usuario:paciente_encontrar_psicologo"))
        self.assertContains(response, 'class="admin-status-dot"', html=False)

    def test_patient_login_redirects_to_patient_panel(self):
        response = self.client.post(
            reverse("login"),
            data={"username": "33111222", "password": "ClaveSegura123"},
        )

        self.assertRedirects(response, reverse("panel_paciente"))


class LogoutFlowTests(TestCase):
    def test_post_logout_closes_session_and_redirects_to_login(self):
        user = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="ClaveSegura123",
        )
        user.is_staff = True
        user.save()
        self.client.force_login(user)

        response = self.client.post(reverse("logout"))

        self.assertRedirects(response, reverse("login"))
        self.assertNotIn("_auth_user_id", self.client.session)


class InactiveProfileLoginTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.ocupacion = Ocupacion.objects.create(
            dsc_ocupacion="ESTUDIANTE",
            flg_activo=True,
        )
        self.grado_estudio = GradoEstudio.objects.create(
            dsc_grado_estudio="SECUNDARIO",
            flg_activo=True,
        )
        self.ciclo_vida = CicloVida.objects.create(
            dsc_ciclo_vida="ADULTEZ INICIAL",
            flg_activo=True,
        )

    def test_inactive_psicologo_cannot_log_in(self):
        Psicologo.objects.create(
            nombres="Laura Psicologa",
            email="laura@example.com",
            dni=31111222,
            cuil=20311112229,
            fch_nacimiento=date(1988, 6, 10),
            id_estado=self.estado_inactivo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )
        get_user_model().objects.create_user(
            username="31111222",
            email="laura@example.com",
            password="ClaveSegura123",
        )

        self.assertIsNone(authenticate(username="31111222", password="ClaveSegura123"))

        response = self.client.post(
            reverse("login"),
            data={"username": "31111222", "password": "ClaveSegura123"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Tu cuenta esta inactiva. Comunicate con administracion para volver a habilitarla.",
        )
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_inactive_paciente_cannot_authenticate(self):
        Paciente.objects.create(
            nombres="Pedro Paciente",
            email="pedro@example.com",
            dni=32111222,
            cuil=20321112221,
            fch_nacimiento=date(2000, 1, 15),
            id_estado=self.estado_inactivo,
            id_ocupacion=self.ocupacion,
            id_ciclo_vida=self.ciclo_vida,
            id_grado_estudio=self.grado_estudio,
        )
        get_user_model().objects.create_user(
            username="32111222",
            email="pedro@example.com",
            password="ClaveSegura123",
        )

        self.assertIsNone(authenticate(username="32111222", password="ClaveSegura123"))

    def test_active_paciente_can_authenticate(self):
        Paciente.objects.create(
            nombres="Paula Paciente",
            email="paula@example.com",
            dni=33111222,
            cuil=20331112220,
            fch_nacimiento=date(1998, 4, 20),
            id_estado=self.estado_activo,
            id_ocupacion=self.ocupacion,
            id_ciclo_vida=self.ciclo_vida,
            id_grado_estudio=self.grado_estudio,
        )
        user = get_user_model().objects.create_user(
            username="33111222",
            email="paula@example.com",
            password="ClaveSegura123",
        )

        self.assertEqual(authenticate(username="33111222", password="ClaveSegura123"), user)
