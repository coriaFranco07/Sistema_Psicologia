from datetime import date

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase
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
from .models import Paciente, Psicologo


class PersonaFormWizardTests(TestCase):
    def assert_wizard_response(self, url_name):
        response = self.client.get(reverse(url_name))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<header>", html=False)
        self.assertNotContains(response, 'name="id_estado"', html=False)
        self.assertContains(response, "Paso 1 de")
        self.assertContains(response, "Datos basicos")
        self.assertContains(response, "Contrasena")
        self.assertContains(response, "Confirmar contrasena")
        self.assertContains(response, "data-password-toggle")
        self.assertContains(response, "Las contrasenas no coinciden.")
        self.assertContains(response, "Siguiente")
        self.assertContains(response, "La foto es opcional: podes dejarla vacia.")

    def test_paciente_create_uses_multistep_layout_without_header(self):
        response = self.client.get(reverse("usuario:paciente_create"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<header>", html=False)
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

    def test_psicologo_create_uses_multistep_layout_without_header(self):
        self.assert_wizard_response("usuario:psicologo_create")


class PersonaListLayoutTests(TestCase):
    def assert_modern_list_response(self, url_name):
        response = self.client.get(reverse(url_name))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "<header>", html=False)
        self.assertContains(response, "modern-table")
        self.assertContains(response, "list-toolbar")
        self.assertContains(response, "registros encontrados")

    def test_paciente_list_uses_modern_layout_without_header(self):
        self.assert_modern_list_response("usuario:paciente_list")

    def test_psicologo_list_uses_modern_layout_without_header(self):
        self.assert_modern_list_response("usuario:psicologo_list")


class PersonaFormDefaultsTests(TestCase):
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
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
        psicologo = form.save()
        form.save_auth_user(psicologo)

        self.assertEqual(psicologo.id_estado, estado_activo)
        self.assertTrue(get_user_model().objects.filter(username="30111222").exists())


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

    def test_create_psicologo_from_view_without_estado_or_foto(self):
        response = self.client.post(
            reverse("usuario:psicologo_create"),
            data={
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
            },
        )

        if response.status_code != 302:
            self.fail(
                f"Form errors: {response.context['form'].errors}; "
                f"datos_form errors: {response.context['datos_form'].errors}"
            )
        self.assertRedirects(response, reverse("usuario:psicologo_list"))

        psicologo = Psicologo.objects.get(dni=31111222)
        self.assertEqual(psicologo.id_estado, self.estado_activo)
        self.assertFalse(psicologo.foto)
        self.assertTrue(DatosPersonales.objects.filter(psicologo=psicologo).exists())

        user = get_user_model().objects.get(username="31111222")
        self.assertEqual(user.email, "laura@example.com")
        self.assertTrue(user.check_password("ClaveSegura123"))
        self.assertEqual(authenticate(username="31111222", password="ClaveSegura123"), user)
