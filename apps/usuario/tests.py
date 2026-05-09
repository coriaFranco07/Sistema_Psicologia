from datetime import date

from django.contrib.auth import authenticate, get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.datos_personales.models import DatosPersonales
from apps.parametro.models import (
    CicloVida,
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

from .forms import PacienteForm, PsicologoForm
from .models import Paciente, Psicologo, PsicologoPendiente


TEST_STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def titulo_pdf_upload(name="titulo.pdf"):
    return SimpleUploadedFile(
        name,
        b"%PDF-1.4\n% Titulo profesional de prueba\n",
        content_type="application/pdf",
    )


def foto_upload(name="perfil.png"):
    return SimpleUploadedFile(
        name,
        b"archivo-imagen-prueba",
        content_type="image/png",
    )


class UsuarioFormWizardTests(TestCase):
    def assert_wizard_response(self, url_name, template_name):
        response = self.client.get(reverse(url_name))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertContains(response, "Panel de administracion")
        self.assertContains(response, "data-admin-sidebar-toggle")
        self.assertContains(response, "data-admin-section-toggle")
        self.assertContains(response, "Psicologos")
        self.assertContains(response, "Pacientes")
        self.assertContains(response, "Ver psicologos")
        self.assertNotContains(response, 'name="id_estado"', html=False)
        self.assertContains(response, "Paso 1 de")
        self.assertContains(response, "Datos basicos")
        self.assertContains(response, "Contrasena")
        self.assertContains(response, "Confirmar contrasena")
        self.assertContains(response, "data-password-toggle")
        self.assertContains(response, "Las contrasenas no coinciden.")
        self.assertContains(response, "Siguiente")
        self.assertContains(response, "La foto es opcional: podes dejarla vacia.")

    def test_paciente_create_uses_multistep_layout_with_admin_panel(self):
        response = self.client.get(reverse("usuario:paciente_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/paciente_form.html")
        self.assertContains(response, "Panel de administracion")
        self.assertNotContains(response, 'name="id_estado"', html=False)
        self.assertNotContains(response, 'name="id_ciclo_vida"', html=False)
        self.assertContains(response, "Paso 1 de")
        self.assertContains(response, "Datos basicos")
        self.assertContains(response, "Contrasena")
        self.assertContains(response, "Confirmar contrasena")
        self.assertContains(response, "data-password-toggle")
        self.assertContains(response, "Las contrasenas no coinciden.")
        self.assertContains(response, "Siguiente")
        self.assertContains(response, "La foto es opcional: podes dejarla vacia.")
        self.assertContains(response, "calcula automaticamente el ciclo de vida")

    def test_psicologo_create_uses_multistep_layout_with_admin_panel(self):
        self.assert_wizard_response("usuario:psicologo_create", "psicologo/psicologo_form.html")
        response = self.client.get(reverse("usuario:psicologo_create"))
        self.assertContains(response, 'name="titulo"', html=False)
        self.assertContains(response, "Adjunta el titulo profesional en formato PDF")


class UsuarioListLayoutTests(TestCase):
    def assert_modern_list_response(self, url_name, template_name):
        response = self.client.get(reverse(url_name))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, template_name)
        self.assertContains(response, "Panel de administracion")
        self.assertContains(response, "data-admin-section-toggle")
        self.assertContains(response, "Psicologos pendientes")
        self.assertContains(response, "modern-table")
        self.assertContains(response, "list-toolbar")
        self.assertContains(response, "registros encontrados")

    def test_paciente_list_uses_modern_layout_with_admin_panel(self):
        self.assert_modern_list_response("usuario:paciente_list", "paciente/paciente_list.html")

    def test_psicologo_list_uses_modern_layout_with_admin_panel(self):
        self.assert_modern_list_response("usuario:psicologo_list", "psicologo/psicologo_list.html")


@override_settings(STORAGES=TEST_STORAGES)
class PsicologoFormDefaultsTests(TestCase):
    def test_psicologo_form_assigns_activo_by_default(self):
        estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        form = PsicologoForm(
            data={
                "nombres": "Ana Profesional",
                "email": "ana@example.com",
                "dni": "30111222",
                "cuil": "20301112229",
                "fch_nacimiento": "1990-01-15",
                "id_rama": rama.pk,
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            },
            files={"titulo": titulo_pdf_upload()},
        )

        self.assertTrue(form.is_valid(), form.errors)
        psicologo = form.save()
        form.save_auth_user(psicologo)

        self.assertEqual(psicologo.id_estado, estado_activo)
        self.assertTrue(psicologo.titulo)
        self.assertTrue(get_user_model().objects.filter(username="30111222").exists())

    def test_psicologo_form_requires_titulo_pdf(self):
        Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        form = PsicologoForm(
            data={
                "nombres": "Ana Profesional",
                "email": "ana@example.com",
                "dni": "30111222",
                "cuil": "20301112229",
                "fch_nacimiento": "1990-01-15",
                "id_rama": Rama.objects.get(dsc_rama="CLINICA").pk,
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)

    def test_psicologo_form_rejects_non_pdf_titulo(self):
        Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        form = PsicologoForm(
            data={
                "nombres": "Ana Profesional",
                "email": "ana@example.com",
                "dni": "30111222",
                "cuil": "20301112229",
                "fch_nacimiento": "1990-01-15",
                "id_rama": rama.pk,
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            },
            files={
                "titulo": SimpleUploadedFile(
                    "titulo.txt",
                    b"no es pdf",
                    content_type="text/plain",
                )
            },
        )

        self.assertFalse(form.is_valid())
        self.assertIn("titulo", form.errors)


class PacienteAutoCicloVidaTests(TestCase):
    @staticmethod
    def birth_date_for_age(age):
        today = date.today()
        try:
            return today.replace(year=today.year - age)
        except ValueError:
            return today.replace(year=today.year - age, month=2, day=28)

    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.ocupacion = Ocupacion.objects.create(dsc_ocupacion="ESTUDIANTE", flg_activo=True)
        self.grado_estudio = GradoEstudio.objects.create(
            dsc_grado_estudio="SECUNDARIO",
            flg_activo=True,
        )
        for descripcion in (
            "INFANCIA",
            "ADOLESCENCIA",
            "ADULTEZ INICIAL",
            "ADULTEZ MADURA",
            "VEJEZ",
        ):
            CicloVida.objects.get_or_create(
                dsc_ciclo_vida=descripcion,
                defaults={"flg_activo": True},
            )

    def test_paciente_form_assigns_ciclo_vida_according_to_birth_date(self):
        casos = (
            (10, "INFANCIA"),
            (17, "ADOLESCENCIA"),
            (39, "ADULTEZ INICIAL"),
            (59, "ADULTEZ MADURA"),
            (60, "VEJEZ"),
        )

        for indice, (edad, descripcion) in enumerate(casos, start=1):
            dni = 30_000_000 + indice
            form = PacienteForm(
                data={
                    "nombres": f"Paciente {edad}",
                    "email": f"paciente{indice}@example.com",
                    "dni": str(dni),
                    "cuil": f"20{dni:08d}{indice}",
                    "fch_nacimiento": self.birth_date_for_age(edad).isoformat(),
                    "id_ocupacion": self.ocupacion.pk,
                    "id_grado_estudio": self.grado_estudio.pk,
                    "password1": "ClaveSegura123",
                    "password2": "ClaveSegura123",
                }
            )

            with self.subTest(edad=edad, descripcion=descripcion):
                self.assertTrue(form.is_valid(), form.errors)
                paciente = form.save()
                self.assertEqual(paciente.id_estado, self.estado_activo)
                self.assertEqual(paciente.id_ciclo_vida.dsc_ciclo_vida, descripcion)


class PacienteCreateViewTests(TestCase):
    @staticmethod
    def birth_date_for_age(age):
        today = date.today()
        try:
            return today.replace(year=today.year - age)
        except ValueError:
            return today.replace(year=today.year - age, month=2, day=28)

    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.sexo = Sexo.objects.create(dsc_tipo="MASCULINO", flg_activo=True)
        self.estado_civil = TipoCivil.objects.create(dsc_std_civil="SOLTERO", flg_activo=True)
        self.pais = Pais.objects.create(dsc_pais="ARGENTINA", flg_activo=True)
        self.provincia = Provincia.objects.create(dsc_provincia="CORDOBA", flg_activo=True)
        self.localidad = Localidad.objects.create(dsc_localidad="CORDOBA", flg_activo=True)
        self.zona = Zona.objects.create(dsc_zona="CENTRO", flg_activo=True)
        self.ocupacion = Ocupacion.objects.create(dsc_ocupacion="ESTUDIANTE", flg_activo=True)
        self.grado_estudio = GradoEstudio.objects.create(
            dsc_grado_estudio="SECUNDARIO",
            flg_activo=True,
        )
        for descripcion in (
            "INFANCIA",
            "ADOLESCENCIA",
            "ADULTEZ INICIAL",
            "ADULTEZ MADURA",
            "VEJEZ",
        ):
            CicloVida.objects.get_or_create(
                dsc_ciclo_vida=descripcion,
                defaults={"flg_activo": True},
            )

    def test_create_paciente_assigns_ciclo_vida_from_birth_date(self):
        response = self.client.post(
            reverse("usuario:paciente_create"),
            data={
                "nombres": "Pedro Paciente",
                "email": "pedro@example.com",
                "dni": "32111222",
                "cuil": "20321112221",
                "fch_nacimiento": self.birth_date_for_age(17).isoformat(),
                "id_ocupacion": self.ocupacion.pk,
                "id_grado_estudio": self.grado_estudio.pk,
                "telefono": "3515551234",
                "domicilio": "San Martin 123",
                "id_sexo": self.sexo.pk,
                "id_std_civil": self.estado_civil.pk,
                "id_pais": self.pais.pk,
                "id_provincia": self.provincia.pk,
                "id_localidad": self.localidad.pk,
                "id_zona": self.zona.pk,
                "password1": "ClaveSegura123",
                "password2": "ClaveSegura123",
            },
        )

        if response.status_code != 302:
            self.fail(
                f"Form errors: {response.context['form'].errors}; "
                f"datos_form errors: {response.context['datos_form'].errors}"
            )
        self.assertRedirects(response, reverse("usuario:paciente_list"))

        paciente = Paciente.objects.get(dni=32111222)
        self.assertEqual(paciente.id_estado, self.estado_activo)
        self.assertEqual(paciente.id_ciclo_vida.dsc_ciclo_vida, "ADOLESCENCIA")
        self.assertTrue(DatosPersonales.objects.filter(paciente=paciente).exists())


@override_settings(STORAGES=TEST_STORAGES)
class PsicologoCreateViewTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.sexo = Sexo.objects.create(dsc_tipo="FEMENINO", flg_activo=True)
        self.estado_civil = TipoCivil.objects.create(dsc_std_civil="SOLTERO", flg_activo=True)
        self.pais = Pais.objects.create(dsc_pais="ARGENTINA", flg_activo=True)
        self.provincia = Provincia.objects.create(dsc_provincia="CORDOBA", flg_activo=True)
        self.localidad = Localidad.objects.create(dsc_localidad="CORDOBA", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.zona = Zona.objects.create(dsc_zona="CENTRO", flg_activo=True)

    def psicologo_payload(self, include_titulo=True, include_foto=False):
        payload = {
            "nombres": "Laura Psicologa",
            "email": "laura@example.com",
            "dni": "31111222",
            "cuil": "20311112229",
            "fch_nacimiento": "1988-06-10",
            "id_rama": self.rama.pk,
            "telefono": "3515551234",
            "domicilio": "San Martin 123",
            "id_sexo": self.sexo.pk,
            "id_std_civil": self.estado_civil.pk,
            "id_pais": self.pais.pk,
            "id_provincia": self.provincia.pk,
            "id_localidad": self.localidad.pk,
            "id_zona": self.zona.pk,
            "password1": "ClaveSegura123",
            "password2": "ClaveSegura123",
        }
        if include_titulo:
            payload["titulo"] = titulo_pdf_upload()
        if include_foto:
            payload["foto"] = foto_upload()
        return payload

    def create_solicitud(self, include_foto=False):
        response = self.client.post(
            reverse("usuario:psicologo_create"),
            data=self.psicologo_payload(include_foto=include_foto),
        )

        if response.status_code != 302:
            self.fail(
                f"Form errors: {response.context['form'].errors}; "
                f"datos_form errors: {response.context['datos_form'].errors}"
            )
        return response

    def test_create_psicologo_request_goes_to_pending_table(self):
        response = self.create_solicitud()
        self.assertRedirects(response, reverse("usuario:psicologo_pendiente_list"))

        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.assertEqual(solicitud.estado, PsicologoPendiente.ESTADO_PENDIENTE)
        self.assertEqual(solicitud.id_rama, self.rama)
        self.assertTrue(solicitud.titulo)
        self.assertFalse(solicitud.foto)
        self.assertNotEqual(solicitud.password_hash, "ClaveSegura123")
        self.assertFalse(Psicologo.objects.filter(dni=31111222).exists())
        self.assertFalse(get_user_model().objects.filter(username="31111222").exists())

    def test_confirm_pending_psicologo_creates_real_psicologo(self):
        self.create_solicitud()
        solicitud = PsicologoPendiente.objects.get(dni=31111222)

        response = self.client.post(
            reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk])
        )

        self.assertRedirects(response, reverse("usuario:psicologo_pendiente_list"))

        solicitud.refresh_from_db()
        psicologo = Psicologo.objects.get(dni=31111222)
        self.assertEqual(solicitud.estado, PsicologoPendiente.ESTADO_APROBADO)
        self.assertEqual(solicitud.psicologo, psicologo)
        self.assertEqual(psicologo.id_estado, self.estado_activo)
        self.assertTrue(psicologo.titulo)
        self.assertFalse(psicologo.foto)
        self.assertTrue(DatosPersonales.objects.filter(psicologo=psicologo).exists())

        user = get_user_model().objects.get(username="31111222")
        self.assertEqual(user.email, "laura@example.com")
        self.assertTrue(user.check_password("ClaveSegura123"))
        self.assertEqual(authenticate(username="31111222", password="ClaveSegura123"), user)

    def test_reject_pending_psicologo_does_not_create_real_psicologo(self):
        self.create_solicitud()
        solicitud = PsicologoPendiente.objects.get(dni=31111222)

        response = self.client.post(
            reverse("usuario:psicologo_pendiente_rechazar", args=[solicitud.pk])
        )

        self.assertRedirects(response, reverse("usuario:psicologo_pendiente_list"))
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, PsicologoPendiente.ESTADO_RECHAZADO)
        self.assertFalse(Psicologo.objects.filter(dni=31111222).exists())
        self.assertFalse(get_user_model().objects.filter(username="31111222").exists())

    def test_create_psicologo_without_titulo_does_not_submit(self):
        response = self.client.post(
            reverse("usuario:psicologo_create"),
            data=self.psicologo_payload(include_titulo=False),
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Psicologo.objects.filter(dni=31111222).exists())
        self.assertFalse(PsicologoPendiente.objects.filter(dni=31111222).exists())
        self.assertIn("titulo", response.context["form"].errors)

    def test_pending_psicologo_list_uses_review_template(self):
        response = self.client.get(reverse("usuario:psicologo_pendiente_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "psicologo/psicologo_pendiente.html")
        self.assertContains(response, "Solicitudes de Psicologos")

    def test_pending_psicologo_list_shows_view_profile_action(self):
        self.create_solicitud()
        solicitud = PsicologoPendiente.objects.get(dni=31111222)

        response = self.client.get(reverse("usuario:psicologo_pendiente_list"))

        self.assertContains(
            response,
            reverse("usuario:psicologo_pendiente_detail", args=[solicitud.pk]),
        )
        self.assertContains(response, "Ver ficha")
        self.assertContains(response, "Aprobar")

    def test_pending_psicologo_detail_displays_full_profile(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)

        response = self.client.get(reverse("usuario:psicologo_pendiente_detail", args=[solicitud.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "psicologo/psicologo_pendiente_detail.html")
        self.assertContains(response, "Solicitud de Laura Psicologa")
        self.assertContains(response, "Foto de perfil de Laura Psicologa")
        self.assertContains(response, "laura@example.com")
        self.assertContains(response, "3515551234")
        self.assertContains(response, "San Martin 123")
        self.assertContains(response, "Abrir PDF adjunto")

    def test_psicologo_list_shows_complete_data_and_view_profile_action(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)

        response = self.client.get(reverse("usuario:psicologo_list"))

        self.assertContains(response, "Laura Psicologa")
        self.assertContains(response, "3515551234")
        self.assertContains(response, "CORDOBA")
        self.assertContains(response, "CLINICA")
        self.assertContains(response, "Acciones")
        self.assertContains(response, reverse("usuario:psicologo_detail", args=[psicologo.pk]))
        self.assertContains(response, "Ver ficha")

    def test_psicologo_detail_displays_full_profile(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)

        response = self.client.get(reverse("usuario:psicologo_detail", args=[psicologo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "psicologo/psicologo_detail.html")
        self.assertContains(response, "Psicologo Laura Psicologa")
        self.assertContains(response, "Foto de perfil de Laura Psicologa")
        self.assertContains(response, "laura@example.com")
        self.assertContains(response, "3515551234")
        self.assertContains(response, "San Martin 123")
        self.assertContains(response, "Abrir PDF adjunto")
