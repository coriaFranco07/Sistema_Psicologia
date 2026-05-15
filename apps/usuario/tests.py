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
    Idioma,
    Localidad,
    MetodoPago,
    Ocupacion,
    Pais,
    Provincia,
    Rama,
    Sexo,
    TipoCivil,
    Zona,
)

from .forms import PacienteForm, PsicologoForm
from .models import (
    Paciente,
    Psicologo,
    PsicologoIdioma,
    PsicologoMetodoPago,
    PsicologoOficina,
    PsicologoPendiente,
    PsicologoRama,
)


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


def create_staff_user(username="admin", email="admin@example.com", password="ClaveSegura123"):
    user = get_user_model().objects.create_user(
        username=username,
        email=email,
        password=password,
    )
    user.is_staff = True
    user.save()
    return user


class UsuarioFormWizardTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user()
        self.client.force_login(self.staff_user)

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
    def setUp(self):
        self.staff_user = create_staff_user()
        self.client.force_login(self.staff_user)

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


class UsuarioAuthProtectionTests(TestCase):
    def assert_login_redirect(self, response, path):
        expected = f"{reverse('login')}?next={path}"
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], expected)

    def test_anonymous_user_is_redirected_from_protected_get_routes(self):
        protected_routes = (
            ("panel_admin", {}),
            ("panel_psicologo", {}),
            ("panel_paciente", {}),
            ("usuario:psicologo_list", {}),
            ("usuario:psicologo_create", {}),
            ("usuario:psicologo_mi_perfil", {}),
            ("usuario:psicologo_detail", {"pk": 1}),
            ("usuario:psicologo_pendiente_list", {}),
            ("usuario:psicologo_pendiente_detail", {"pk": 1}),
            ("usuario:psicologo_update", {"pk": 1}),
            ("usuario:psicologo_delete", {"pk": 1}),
            ("usuario:psicologo_oficina_list", {}),
            ("usuario:psicologo_oficina_create", {}),
            ("usuario:psicologo_oficina_update", {"pk": 1}),
            ("usuario:psicologo_oficina_delete", {"pk": 1}),
            ("usuario:psicologo_metodo_pago_list", {}),
            ("usuario:psicologo_metodo_pago_create", {}),
            ("usuario:psicologo_metodo_pago_update", {"pk": 1}),
            ("usuario:psicologo_metodo_pago_delete", {"pk": 1}),
            ("usuario:psicologo_rama_list", {}),
            ("usuario:psicologo_rama_create", {}),
            ("usuario:psicologo_rama_update", {"pk": 1}),
            ("usuario:psicologo_rama_delete", {"pk": 1}),
            ("usuario:psicologo_idioma_list", {}),
            ("usuario:psicologo_idioma_create", {}),
            ("usuario:psicologo_idioma_update", {"pk": 1}),
            ("usuario:psicologo_idioma_delete", {"pk": 1}),
            ("usuario:paciente_list", {}),
            ("usuario:paciente_create", {}),
            ("usuario:paciente_mi_perfil", {}),
            ("usuario:paciente_mis_psicologos", {}),
            ("usuario:paciente_encontrar_psicologo", {}),
            ("usuario:paciente_detail", {"pk": 1}),
            ("usuario:paciente_update", {"pk": 1}),
            ("usuario:paciente_delete", {"pk": 1}),
        )

        for route_name, kwargs in protected_routes:
            with self.subTest(route=route_name):
                path = reverse(route_name, kwargs=kwargs)
                response = self.client.get(path)
                self.assert_login_redirect(response, path)

    def test_anonymous_user_is_redirected_from_protected_post_routes(self):
        protected_routes = (
            ("usuario:psicologo_create", {}),
            ("usuario:psicologo_pendiente_confirmar", {"pk": 1}),
            ("usuario:psicologo_pendiente_rechazar", {"pk": 1}),
            ("usuario:paciente_create", {}),
        )

        for route_name, kwargs in protected_routes:
            with self.subTest(route=route_name):
                path = reverse(route_name, kwargs=kwargs)
                response = self.client.post(path, data={})
                self.assert_login_redirect(response, path)


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
                "ramas": [rama.pk],
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
        self.assertTrue(psicologo.ramas.filter(id_rama=rama, id_estado=estado_activo).exists())
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
                "ramas": [Rama.objects.get(dsc_rama="CLINICA").pk],
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
                "ramas": [rama.pk],
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
        self.staff_user = create_staff_user()
        self.client.force_login(self.staff_user)
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
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

    def create_patient_with_profile(self):
        paciente = Paciente.objects.create(
            nombres="Pedro Paciente",
            email="pedro@example.com",
            dni=32111222,
            cuil=20321112221,
            fch_nacimiento=date(2000, 1, 15),
            id_estado=self.estado_activo,
            id_ocupacion=self.ocupacion,
            id_ciclo_vida=CicloVida.objects.get(dsc_ciclo_vida="ADULTEZ INICIAL"),
            id_grado_estudio=self.grado_estudio,
        )
        DatosPersonales.objects.create(
            paciente=paciente,
            telefono="3515551234",
            domicilio="San Martin 123",
            id_sexo=self.sexo,
            id_std_civil=self.estado_civil,
            id_pais=self.pais,
            id_provincia=self.provincia,
            id_localidad=self.localidad,
            id_zona=self.zona,
        )
        return paciente

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

    def test_paciente_list_shows_view_profile_action(self):
        paciente = self.create_patient_with_profile()

        response = self.client.get(reverse("usuario:paciente_list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ver ficha")
        self.assertContains(response, reverse("usuario:paciente_detail", args=[paciente.pk]))

    def test_paciente_detail_displays_full_profile(self):
        paciente = self.create_patient_with_profile()

        response = self.client.get(reverse("usuario:paciente_detail", args=[paciente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/paciente_detail.html")
        self.assertContains(response, "Paciente Pedro Paciente")
        self.assertContains(response, "Foto de perfil de Pedro Paciente")
        self.assertContains(response, "pedro@example.com")
        self.assertContains(response, "3515551234")
        self.assertContains(response, "San Martin 123")
        self.assertContains(response, "ESTUDIANTE")
        self.assertContains(response, "ADULTEZ INICIAL")

    def test_paciente_mi_perfil_redirects_to_logged_patient_detail(self):
        paciente = self.create_patient_with_profile()
        user = get_user_model().objects.create_user(
            username=str(paciente.dni),
            email=paciente.email,
            password="ClaveSegura123",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("usuario:paciente_mi_perfil"))

        self.assertRedirects(response, reverse("usuario:paciente_detail", args=[paciente.pk]))

    def test_paciente_confirm_delete_uses_inactivation_copy(self):
        paciente = self.create_patient_with_profile()

        response = self.client.get(reverse("usuario:paciente_delete", args=[paciente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inactivar paciente")
        self.assertContains(response, "dar de baja")
        self.assertContains(response, "Inactivar")

    def test_paciente_delete_sets_inactive_state(self):
        paciente = self.create_patient_with_profile()

        response = self.client.post(reverse("usuario:paciente_delete", args=[paciente.pk]))

        self.assertRedirects(response, reverse("usuario:paciente_list"))
        paciente.refresh_from_db()
        self.assertEqual(paciente.id_estado, self.estado_inactivo)

    def test_paciente_list_shows_activate_action_for_inactive_records(self):
        paciente = self.create_patient_with_profile()
        paciente.id_estado = self.estado_inactivo
        paciente.save(update_fields=["id_estado"])

        response = self.client.get(reverse("usuario:paciente_list"))

        self.assertContains(response, reverse("usuario:paciente_delete", args=[paciente.pk]))
        self.assertContains(response, "Activar")

    def test_paciente_confirm_delete_uses_activation_copy_for_inactive_patient(self):
        paciente = self.create_patient_with_profile()
        paciente.id_estado = self.estado_inactivo
        paciente.save(update_fields=["id_estado"])

        response = self.client.get(reverse("usuario:paciente_delete", args=[paciente.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar paciente")
        self.assertContains(response, "volver a activar")

    def test_paciente_delete_reactivates_inactive_state(self):
        paciente = self.create_patient_with_profile()
        paciente.id_estado = self.estado_inactivo
        paciente.save(update_fields=["id_estado"])

        response = self.client.post(reverse("usuario:paciente_delete", args=[paciente.pk]))

        self.assertRedirects(response, reverse("usuario:paciente_list"))
        paciente.refresh_from_db()
        self.assertEqual(paciente.id_estado, self.estado_activo)


class PacientePsychologistSectionsTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.rama_secundaria = Rama.objects.create(dsc_rama="INFANTIL", flg_activo=True)
        self.pais = Pais.objects.create(dsc_pais="ARGENTINA", flg_activo=True)
        self.provincia = Provincia.objects.create(dsc_provincia="CORDOBA", flg_activo=True)
        self.localidad = Localidad.objects.create(dsc_localidad="CORDOBA", flg_activo=True)
        self.zona = Zona.objects.create(dsc_zona="CENTRO", flg_activo=True)
        self.idioma_es = Idioma.objects.create(dsc_idioma="ESPANOL", flg_activo=True)
        self.idioma_en = Idioma.objects.create(dsc_idioma="INGLES", flg_activo=True)
        self.ocupacion = Ocupacion.objects.create(dsc_ocupacion="ESTUDIANTE", flg_activo=True)
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
            username=str(self.paciente.dni),
            email=self.paciente.email,
            password="ClaveSegura123",
        )

        self.psicologo_activo = Psicologo.objects.create(
            nombres="Laura Psicologa",
            email="laura@example.com",
            dni=31111222,
            cuil=20311112229,
            fch_nacimiento=date(1988, 6, 10),
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )
        self.psicologo_virtual = Psicologo.objects.create(
            nombres="Sofia Virtual",
            email="sofia@example.com",
            dni=32111222,
            cuil=20321112229,
            fch_nacimiento=date(1990, 8, 11),
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test3.pdf",
        )
        self.psicologo_inactivo = Psicologo.objects.create(
            nombres="Mario Inactivo",
            email="mario@example.com",
            dni=30111222,
            cuil=20301112229,
            fch_nacimiento=date(1985, 2, 14),
            id_estado=self.estado_inactivo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test2.pdf",
        )
        PsicologoOficina.objects.create(
            id_psicologo=self.psicologo_activo,
            domicilio="San Martin 123",
            telefono="3515551234",
            id_pais=self.pais,
            id_provincia=self.provincia,
            id_localidad=self.localidad,
            id_zona=self.zona,
            id_estado=self.estado_activo,
        )
        PsicologoIdioma.objects.create(
            id_psicologo=self.psicologo_activo,
            id_idioma=self.idioma_es,
            id_estado=self.estado_activo,
        )
        PsicologoIdioma.objects.create(
            id_psicologo=self.psicologo_activo,
            id_idioma=self.idioma_en,
            id_estado=self.estado_activo,
        )
        PsicologoIdioma.objects.create(
            id_psicologo=self.psicologo_virtual,
            id_idioma=self.idioma_es,
            id_estado=self.estado_activo,
        )
        PsicologoRama.objects.create(
            id_psicologo=self.psicologo_activo,
            id_rama=self.rama_secundaria,
            valor_sesion=0,
            id_estado=self.estado_activo,
        )

        self.client.force_login(self.user)

    def test_mis_psicologos_page_shows_placeholder(self):
        response = self.client.get(reverse("usuario:paciente_mis_psicologos"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/mis_psicologos.html")
        self.assertContains(response, "Aun no tienes psicologos vinculados.")
        self.assertContains(response, reverse("usuario:paciente_encontrar_psicologo"))

    def test_encontrar_psicologo_lists_only_active_psychologists(self):
        response = self.client.get(reverse("usuario:paciente_encontrar_psicologo"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "paciente/encontrar_psicologo.html")
        self.assertContains(response, "Encuentra un profesional activo que encaje contigo.")
        self.assertContains(response, self.psicologo_activo.nombres)
        self.assertContains(response, self.psicologo_virtual.nombres)
        self.assertContains(response, self.psicologo_activo.id_rama.dsc_rama)
        self.assertContains(response, reverse("usuario:psicologo_detail", args=[self.psicologo_activo.pk]))
        self.assertContains(response, "Sesiones virtuales y presenciales")
        self.assertContains(response, "Sesiones virtuales")
        self.assertContains(response, self.idioma_es.dsc_idioma)
        self.assertContains(response, self.idioma_en.dsc_idioma)
        self.assertNotContains(response, self.psicologo_inactivo.nombres)
        self.assertNotContains(response, "modern-table")

    def test_encontrar_psicologo_filters_by_query(self):
        response = self.client.get(
            reverse("usuario:paciente_encontrar_psicologo"),
            {"q": "Laura"},
        )

        self.assertContains(response, self.psicologo_activo.nombres)
        self.assertNotContains(response, self.psicologo_inactivo.nombres)
        self.assertContains(response, 'value="Laura"', html=False)

    def test_encontrar_psicologo_filters_by_modalidad_presencial(self):
        response = self.client.get(
            reverse("usuario:paciente_encontrar_psicologo"),
            {"modalidad": "presencial"},
        )

        self.assertContains(response, self.psicologo_activo.nombres)
        self.assertNotContains(response, self.psicologo_virtual.nombres)

    def test_encontrar_psicologo_filters_by_provincia(self):
        response = self.client.get(
            reverse("usuario:paciente_encontrar_psicologo"),
            {"provincia": str(self.provincia.pk)},
        )

        self.assertContains(response, self.psicologo_activo.nombres)
        self.assertNotContains(response, self.psicologo_virtual.nombres)

    def test_patient_psicologo_detail_shows_profile_with_cta(self):
        response = self.client.get(
            reverse("usuario:psicologo_detail", args=[self.psicologo_activo.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Foto de Laura Psicologa")
        self.assertContains(response, "Quiero que sea mi psicólogo")
        self.assertContains(response, "Online y presencial")
        self.assertContains(response, "Especialista en clinica, infantil")
        self.assertContains(response, self.idioma_en.dsc_idioma)
        self.assertContains(
            response,
            f"{self.provincia.dsc_provincia}, {self.localidad.dsc_localidad}",
        )
        self.assertNotContains(response, self.psicologo_activo.email)
        self.assertNotContains(response, "3515551234")
        self.assertNotContains(response, "Ver titulo PDF")


@override_settings(STORAGES=TEST_STORAGES)
class PsicologoCreateViewTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user()
        self.client.force_login(self.staff_user)
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.sexo = Sexo.objects.create(dsc_tipo="FEMENINO", flg_activo=True)
        self.estado_civil = TipoCivil.objects.create(dsc_std_civil="SOLTERO", flg_activo=True)
        self.pais = Pais.objects.create(dsc_pais="ARGENTINA", flg_activo=True)
        self.provincia = Provincia.objects.create(dsc_provincia="CORDOBA", flg_activo=True)
        self.localidad = Localidad.objects.create(dsc_localidad="CORDOBA", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.rama_secundaria = Rama.objects.create(dsc_rama="INFANTIL", flg_activo=True)
        self.rama_terciaria = Rama.objects.create(dsc_rama="PAREJA", flg_activo=True)
        self.zona = Zona.objects.create(dsc_zona="CENTRO", flg_activo=True)

    def psicologo_payload(self, include_titulo=True, include_foto=False):
        payload = {
            "nombres": "Laura Psicologa",
            "email": "laura@example.com",
            "dni": "31111222",
            "cuil": "20311112229",
            "fch_nacimiento": "1988-06-10",
            "ramas": [self.rama.pk, self.rama_secundaria.pk],
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

    def create_psicologo_aprobado(self):
        self.create_solicitud()
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        return Psicologo.objects.get(dni=31111222)

    def psicologo_update_payload(self, psicologo, ramas):
        datos = psicologo.datos_personales_rel
        return {
            "nombres": psicologo.nombres,
            "email": psicologo.email,
            "dni": str(psicologo.dni),
            "cuil": str(psicologo.cuil),
            "fch_nacimiento": psicologo.fch_nacimiento.isoformat(),
            "ramas": ramas,
            "sobre_mi": psicologo.sobre_mi,
            "telefono": datos.telefono,
            "domicilio": datos.domicilio,
            "id_sexo": datos.id_sexo_id,
            "id_std_civil": datos.id_std_civil_id,
            "id_pais": datos.id_pais_id,
            "id_provincia": datos.id_provincia_id,
            "id_localidad": datos.id_localidad_id,
            "id_zona": datos.id_zona_id,
            "password1": "",
            "password2": "",
        }

    def test_create_psicologo_request_goes_to_pending_table(self):
        response = self.create_solicitud()
        self.assertRedirects(response, reverse("usuario:psicologo_pendiente_list"))

        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.assertEqual(solicitud.estado, PsicologoPendiente.ESTADO_PENDIENTE)
        self.assertEqual(solicitud.id_rama, self.rama)
        self.assertEqual(
            list(
                solicitud.ramas_pendientes.order_by("id_psico_pend_rama").values_list(
                    "id_rama_id", flat=True
                )
            ),
            [self.rama.pk, self.rama_secundaria.pk],
        )
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
        self.assertEqual(psicologo.ramas.count(), 2)
        self.assertTrue(psicologo.ramas.filter(id_rama=self.rama).exists())
        self.assertTrue(psicologo.ramas.filter(id_rama=self.rama_secundaria).exists())

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

    def test_create_form_uses_rama_checkboxes_and_hides_valor_sesion(self):
        response = self.client.get(reverse("usuario:psicologo_create"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="checkbox"', html=False)
        self.assertContains(response, self.rama.dsc_rama)
        self.assertContains(response, self.rama_secundaria.dsc_rama)
        self.assertNotContains(response, 'name="valor_sesion"', html=False)

    def test_update_form_uses_rama_checkboxes_and_hides_valor_sesion(self):
        psicologo = self.create_psicologo_aprobado()

        response = self.client.get(reverse("usuario:psicologo_update", args=[psicologo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'type="checkbox"', html=False)
        self.assertContains(response, self.rama.dsc_rama)
        self.assertContains(response, self.rama_secundaria.dsc_rama)
        self.assertNotContains(response, 'name="valor_sesion"', html=False)

    def test_update_psicologo_creates_new_active_rama_when_selected(self):
        psicologo = self.create_psicologo_aprobado()

        response = self.client.post(
            reverse("usuario:psicologo_update", args=[psicologo.pk]),
            data=self.psicologo_update_payload(
                psicologo,
                [self.rama.pk, self.rama_secundaria.pk, self.rama_terciaria.pk],
            ),
        )

        self.assertRedirects(response, reverse("usuario:psicologo_list"))
        psicologo.refresh_from_db()
        self.assertTrue(psicologo.ramas.filter(id_rama=self.rama_terciaria).exists())
        self.assertEqual(
            psicologo.ramas.get(id_rama=self.rama_terciaria).id_estado,
            self.estado_activo,
        )

    def test_update_psicologo_inactivates_unchecked_rama(self):
        psicologo = self.create_psicologo_aprobado()

        response = self.client.post(
            reverse("usuario:psicologo_update", args=[psicologo.pk]),
            data=self.psicologo_update_payload(psicologo, [self.rama.pk]),
        )

        self.assertRedirects(response, reverse("usuario:psicologo_list"))
        psicologo.refresh_from_db()
        self.assertEqual(
            psicologo.ramas.get(id_rama=self.rama_secundaria).id_estado,
            self.estado_inactivo,
        )

    def test_update_psicologo_reactivates_existing_inactive_rama_without_duplicate(self):
        psicologo = self.create_psicologo_aprobado()
        rama_relacion = psicologo.ramas.get(id_rama=self.rama_secundaria)
        rama_relacion.id_estado = self.estado_inactivo
        rama_relacion.save(update_fields=["id_estado"])

        response = self.client.post(
            reverse("usuario:psicologo_update", args=[psicologo.pk]),
            data=self.psicologo_update_payload(
                psicologo,
                [self.rama.pk, self.rama_secundaria.pk],
            ),
        )

        self.assertRedirects(response, reverse("usuario:psicologo_list"))
        psicologo.refresh_from_db()
        self.assertEqual(psicologo.ramas.filter(id_rama=self.rama_secundaria).count(), 1)
        self.assertEqual(
            psicologo.ramas.get(id_rama=self.rama_secundaria).id_estado,
            self.estado_activo,
        )

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
        self.assertContains(response, "CLINICA")
        self.assertContains(response, "INFANTIL")
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
        self.assertTemplateUsed(response, "psicologo/psicologo_detail_admin.html")
        self.assertContains(response, "Psicólogo Laura Psicologa")
        self.assertContains(response, "Foto de Laura Psicologa")
        self.assertContains(response, "laura@example.com")
        self.assertContains(response, "3515551234")
        self.assertContains(response, "San Martin 123")
        self.assertContains(response, "CLINICA")
        self.assertContains(response, "INFANTIL")
        self.assertContains(response, "Abrir PDF adjunto")

    def test_psicologo_confirm_delete_uses_inactivation_copy(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)

        response = self.client.get(reverse("usuario:psicologo_delete", args=[psicologo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Inactivar psicologo")
        self.assertContains(response, "dar de baja")
        self.assertContains(response, "Inactivar")

    def test_psicologo_delete_sets_inactive_state(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)

        response = self.client.post(reverse("usuario:psicologo_delete", args=[psicologo.pk]))

        self.assertRedirects(response, reverse("usuario:psicologo_list"))
        psicologo.refresh_from_db()
        self.assertEqual(psicologo.id_estado, self.estado_inactivo)

    def test_psicologo_list_shows_activate_action_for_inactive_records(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)
        psicologo.id_estado = self.estado_inactivo
        psicologo.save(update_fields=["id_estado"])

        response = self.client.get(reverse("usuario:psicologo_list"))

        self.assertContains(response, reverse("usuario:psicologo_delete", args=[psicologo.pk]))
        self.assertContains(response, "Activar")

    def test_psicologo_confirm_delete_uses_activation_copy_for_inactive_psicologo(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)
        psicologo.id_estado = self.estado_inactivo
        psicologo.save(update_fields=["id_estado"])

        response = self.client.get(reverse("usuario:psicologo_delete", args=[psicologo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar psicologo")
        self.assertContains(response, "volver a activar")

    def test_psicologo_delete_reactivates_inactive_state(self):
        self.create_solicitud(include_foto=True)
        solicitud = PsicologoPendiente.objects.get(dni=31111222)
        self.client.post(reverse("usuario:psicologo_pendiente_confirmar", args=[solicitud.pk]))
        psicologo = Psicologo.objects.get(dni=31111222)
        psicologo.id_estado = self.estado_inactivo
        psicologo.save(update_fields=["id_estado"])

        response = self.client.post(reverse("usuario:psicologo_delete", args=[psicologo.pk]))

        self.assertRedirects(response, reverse("usuario:psicologo_list"))
        psicologo.refresh_from_db()
        self.assertEqual(psicologo.id_estado, self.estado_activo)


class PsicologoOficinaListViewTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.pais = Pais.objects.create(dsc_pais="ARGENTINA", flg_activo=True)
        self.provincia = Provincia.objects.create(dsc_provincia="CORDOBA", flg_activo=True)
        self.localidad = Localidad.objects.create(dsc_localidad="CORDOBA", flg_activo=True)
        self.zona = Zona.objects.create(dsc_zona="CENTRO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)

        self.psicologo = Psicologo.objects.create(
            nombres="Laura Psicologa",
            email="laura@example.com",
            dni=31111222,
            cuil=20311112229,
            fch_nacimiento="1988-06-10",
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )
        self.usuario_psicologo = get_user_model().objects.create_user(
            username="31111222",
            email="laura@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff.is_staff = True
        self.usuario_staff.save()

        self.oficina = PsicologoOficina.objects.create(
            id_psicologo=self.psicologo,
            domicilio="San Martin 123",
            telefono="3515551234",
            id_pais=self.pais,
            id_provincia=self.provincia,
            id_localidad=self.localidad,
            id_zona=self.zona,
            id_estado=self.estado_activo,
        )

    def test_staff_sees_psicologo_column_in_office_list(self):
        self.client.force_login(self.usuario_staff)

        response = self.client.get(reverse("usuario:psicologo_oficina_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mostrar_columna_psicologo"])
        self.assertContains(response, 'class="office-person"', html=False)
        self.assertContains(response, "DNI 31111222")
        self.assertContains(response, "Buscar por psic")

    def test_psicologo_does_not_see_psicologo_column_in_office_list(self):
        self.client.force_login(self.usuario_psicologo)

        response = self.client.get(reverse("usuario:psicologo_oficina_list"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["mostrar_columna_psicologo"])
        self.assertNotContains(response, 'class="office-person"', html=False)
        self.assertNotContains(response, "DNI 31111222")
        self.assertNotContains(response, "Laura Psicologa")
        self.assertNotContains(response, "Buscar por psic")
        self.assertContains(response, "San Martin 123")

    def test_office_delete_reactivates_inactive_record(self):
        self.oficina.id_estado = self.estado_inactivo
        self.oficina.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.post(reverse("usuario:psicologo_oficina_delete", args=[self.oficina.pk]))

        self.assertRedirects(response, reverse("usuario:psicologo_oficina_list"))
        self.oficina.refresh_from_db()
        self.assertEqual(self.oficina.id_estado, self.estado_activo)

    def test_office_confirm_delete_uses_activation_copy_for_inactive_record(self):
        self.oficina.id_estado = self.estado_inactivo
        self.oficina.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.get(reverse("usuario:psicologo_oficina_delete", args=[self.oficina.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar consultorio")
        self.assertContains(response, "volvera a activar")


class PsicologoMetodoPagoIdiomaListViewTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.metodo_pago = MetodoPago.objects.create(dsc_met_pago="TRANSFERENCIA", flg_activo=True)
        self.idioma = Idioma.objects.create(dsc_idioma="INGLES", flg_activo=True)

        self.psicologo = Psicologo.objects.create(
            nombres="Laura Psicologa",
            email="laura@example.com",
            dni=31111222,
            cuil=20311112229,
            fch_nacimiento="1988-06-10",
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )
        self.usuario_psicologo = get_user_model().objects.create_user(
            username="31111222",
            email="laura@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff = get_user_model().objects.create_user(
            username="admin",
            email="admin@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff.is_staff = True
        self.usuario_staff.save()

        self.metodo_pago_registro = PsicologoMetodoPago.objects.create(
            id_psicologo=self.psicologo,
            id_metodo_pago=self.metodo_pago,
            id_estado=self.estado_activo,
        )
        self.idioma_registro = PsicologoIdioma.objects.create(
            id_psicologo=self.psicologo,
            id_idioma=self.idioma,
            id_estado=self.estado_activo,
        )

    def test_staff_sees_psicologo_column_in_payment_list(self):
        self.client.force_login(self.usuario_staff)

        response = self.client.get(reverse("usuario:psicologo_metodo_pago_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mostrar_columna_psicologo"])
        self.assertContains(response, 'class="pay-person"', html=False)
        self.assertContains(response, "DNI 31111222")
        self.assertContains(response, "TRANSFERENCIA")

    def test_psicologo_does_not_see_psicologo_column_in_payment_list(self):
        self.client.force_login(self.usuario_psicologo)

        response = self.client.get(reverse("usuario:psicologo_metodo_pago_list"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["mostrar_columna_psicologo"])
        self.assertNotContains(response, 'class="pay-person"', html=False)
        self.assertNotContains(response, "DNI 31111222")
        self.assertNotContains(response, "Laura Psicologa")
        self.assertContains(response, "TRANSFERENCIA")

    def test_staff_sees_psicologo_column_in_language_list(self):
        self.client.force_login(self.usuario_staff)

        response = self.client.get(reverse("usuario:psicologo_idioma_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mostrar_columna_psicologo"])
        self.assertContains(response, 'class="lang-person"', html=False)
        self.assertContains(response, "DNI 31111222")
        self.assertContains(response, "INGLES")

    def test_psicologo_does_not_see_psicologo_column_in_language_list(self):
        self.client.force_login(self.usuario_psicologo)

        response = self.client.get(reverse("usuario:psicologo_idioma_list"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["mostrar_columna_psicologo"])
        self.assertNotContains(response, 'class="lang-person"', html=False)
        self.assertNotContains(response, "DNI 31111222")
        self.assertNotContains(response, "Laura Psicologa")
        self.assertContains(response, "INGLES")

    def test_payment_delete_reactivates_inactive_record(self):
        self.metodo_pago_registro.id_estado = self.estado_inactivo
        self.metodo_pago_registro.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.post(
            reverse("usuario:psicologo_metodo_pago_delete", args=[self.metodo_pago_registro.pk])
        )

        self.assertRedirects(response, reverse("usuario:psicologo_metodo_pago_list"))
        self.metodo_pago_registro.refresh_from_db()
        self.assertEqual(self.metodo_pago_registro.id_estado, self.estado_activo)

    def test_payment_confirm_delete_uses_activation_copy_for_inactive_record(self):
        self.metodo_pago_registro.id_estado = self.estado_inactivo
        self.metodo_pago_registro.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.get(
            reverse("usuario:psicologo_metodo_pago_delete", args=[self.metodo_pago_registro.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar metodo de pago")
        self.assertContains(response, "volvera a activar")

    def test_language_delete_reactivates_inactive_record(self):
        self.idioma_registro.id_estado = self.estado_inactivo
        self.idioma_registro.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.post(
            reverse("usuario:psicologo_idioma_delete", args=[self.idioma_registro.pk])
        )

        self.assertRedirects(response, reverse("usuario:psicologo_idioma_list"))
        self.idioma_registro.refresh_from_db()
        self.assertEqual(self.idioma_registro.id_estado, self.estado_activo)

    def test_language_confirm_delete_uses_activation_copy_for_inactive_record(self):
        self.idioma_registro.id_estado = self.estado_inactivo
        self.idioma_registro.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.get(
            reverse("usuario:psicologo_idioma_delete", args=[self.idioma_registro.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar idioma")
        self.assertContains(response, "volvera a activar")


class PsicologoRamaListViewTests(TestCase):
    def setUp(self):
        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.estado_inactivo = Estado.objects.create(dsc_estado="INACTIVO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)

        self.psicologo = Psicologo.objects.create(
            nombres="Laura Psicologa",
            email="laura.rama@example.com",
            dni=35111222,
            cuil=20351112229,
            fch_nacimiento="1988-06-10",
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )
        self.usuario_psicologo = get_user_model().objects.create_user(
            username="35111222",
            email="laura.rama@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff = get_user_model().objects.create_user(
            username="admin-rama",
            email="admin-rama@example.com",
            password="ClaveSegura123",
        )
        self.usuario_staff.is_staff = True
        self.usuario_staff.save()

        self.psicologo_rama = self.psicologo.ramas.get(id_rama=self.rama)
        self.psicologo_rama.valor_sesion = "26000.00"
        self.psicologo_rama.save(update_fields=["valor_sesion"])

    def test_staff_sees_psicologo_column_in_rama_list(self):
        self.client.force_login(self.usuario_staff)

        response = self.client.get(reverse("usuario:psicologo_rama_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["mostrar_columna_psicologo"])
        self.assertContains(response, 'class="rama-person"', html=False)
        self.assertContains(response, "DNI 35111222")
        self.assertContains(response, "CLINICA")

    def test_psicologo_does_not_see_psicologo_column_in_rama_list(self):
        self.client.force_login(self.usuario_psicologo)

        response = self.client.get(reverse("usuario:psicologo_rama_list"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["mostrar_columna_psicologo"])
        self.assertNotContains(response, 'class="rama-person"', html=False)
        self.assertNotContains(response, "DNI 35111222")
        self.assertNotContains(response, "Laura Psicologa")
        self.assertContains(response, "CLINICA")

    def test_rama_delete_reactivates_inactive_record(self):
        self.psicologo_rama.id_estado = self.estado_inactivo
        self.psicologo_rama.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.post(
            reverse("usuario:psicologo_rama_delete", args=[self.psicologo_rama.pk])
        )

        self.assertRedirects(response, reverse("usuario:psicologo_rama_list"))
        self.psicologo_rama.refresh_from_db()
        self.assertEqual(self.psicologo_rama.id_estado, self.estado_activo)

    def test_rama_confirm_delete_uses_activation_copy_for_inactive_record(self):
        self.psicologo_rama.id_estado = self.estado_inactivo
        self.psicologo_rama.save(update_fields=["id_estado"])
        self.client.force_login(self.usuario_staff)

        response = self.client.get(
            reverse("usuario:psicologo_rama_delete", args=[self.psicologo_rama.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Activar rama profesional")
        self.assertContains(response, "volvera a activar")


class UsuarioListPaginationTests(TestCase):
    def setUp(self):
        self.staff_user = create_staff_user()
        self.client.force_login(self.staff_user)

        self.estado_activo = Estado.objects.create(dsc_estado="ACTIVO", flg_activo=True)
        self.rama = Rama.objects.create(dsc_rama="CLINICA", flg_activo=True)
        self.sexo = Sexo.objects.create(dsc_tipo="FEMENINO", flg_activo=True)
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
        self.ciclo_vida = CicloVida.objects.create(
            dsc_ciclo_vida="ADULTEZ INICIAL",
            flg_activo=True,
        )
        self.metodo_pago = MetodoPago.objects.create(dsc_met_pago="TRANSFERENCIA", flg_activo=True)
        self.idioma = Idioma.objects.create(dsc_idioma="INGLES", flg_activo=True)

        self.psicologo_base = Psicologo.objects.create(
            nombres="Laura Base",
            email="laura.base@example.com",
            dni=31111222,
            cuil=20311112229,
            fch_nacimiento=date(1988, 6, 10),
            id_estado=self.estado_activo,
            id_rama=self.rama,
            titulo="psicologos/titulos/test.pdf",
        )

    @staticmethod
    def build_cuil(dni, suffix):
        return int(f"20{dni}{suffix}")

    def assert_paginated(self, url, context_name, second_page_count=2):
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(response.context["paginator"].per_page, 10)
        self.assertEqual(len(response.context[context_name]), 10)
        self.assertContains(response, "Pagina 1 de 2")

        response_page_2 = self.client.get(url, {"page": 2})

        self.assertEqual(response_page_2.status_code, 200)
        self.assertEqual(response_page_2.context["page_obj"].number, 2)
        self.assertEqual(len(response_page_2.context[context_name]), second_page_count)
        self.assertContains(response_page_2, "Pagina 2 de 2")

    def create_psicologos(self, total):
        for index in range(total):
            dni = 32000000 + index
            Psicologo.objects.create(
                nombres=f"Psicologo {index:02d}",
                email=f"psicologo{index}@example.com",
                dni=dni,
                cuil=self.build_cuil(dni, index % 10),
                fch_nacimiento=date(1990, 1, 1),
                id_estado=self.estado_activo,
                id_rama=self.rama,
                titulo="psicologos/titulos/test.pdf",
            )

    def create_pacientes(self, total):
        for index in range(total):
            dni = 33000000 + index
            Paciente.objects.create(
                nombres=f"Paciente {index:02d}",
                email=f"paciente{index}@example.com",
                dni=dni,
                cuil=self.build_cuil(dni, index % 10),
                fch_nacimiento=date(1993, 1, 1),
                id_estado=self.estado_activo,
                id_ocupacion=self.ocupacion,
                id_ciclo_vida=self.ciclo_vida,
                id_grado_estudio=self.grado_estudio,
            )

    def create_solicitudes(self, total):
        for index in range(total):
            dni = 34000000 + index
            PsicologoPendiente.objects.create(
                nombres=f"Solicitud {index:02d}",
                email=f"solicitud{index}@example.com",
                dni=dni,
                cuil=self.build_cuil(dni, index % 10),
                fch_nacimiento=date(1991, 1, 1),
                id_rama=self.rama,
                titulo="psicologos/titulos/test.pdf",
                telefono="3515551234",
                domicilio=f"Calle {index}",
                id_sexo=self.sexo,
                id_std_civil=self.estado_civil,
                id_pais=self.pais,
                id_provincia=self.provincia,
                id_localidad=self.localidad,
                id_zona=self.zona,
                password_hash="hash-prueba",
            )

    def create_oficinas(self, total):
        for index in range(total):
            PsicologoOficina.objects.create(
                id_psicologo=self.psicologo_base,
                domicilio=f"Consultorio {index:02d}",
                telefono=f"35155512{index:02d}",
                id_pais=self.pais,
                id_provincia=self.provincia,
                id_localidad=self.localidad,
                id_zona=self.zona,
                id_estado=self.estado_activo,
            )

    def create_metodos_pago(self, total):
        for index in range(total):
            metodo = MetodoPago.objects.create(
                dsc_met_pago=f"METODO {index:02d}",
                flg_activo=True,
            )
            PsicologoMetodoPago.objects.create(
                id_psicologo=self.psicologo_base,
                id_metodo_pago=metodo,
                id_estado=self.estado_activo,
            )

    def create_ramas_profesionales(self, total):
        for index in range(total):
            rama = Rama.objects.create(
                dsc_rama=f"RAMA {index:02d}",
                flg_activo=True,
            )
            PsicologoRama.objects.create(
                id_psicologo=self.psicologo_base,
                id_rama=rama,
                valor_sesion=25000 + index,
                id_estado=self.estado_activo,
            )

    def create_idiomas(self, total):
        for index in range(total):
            idioma = Idioma.objects.create(
                dsc_idioma=f"IDIOMA {index:02d}",
                flg_activo=True,
            )
            PsicologoIdioma.objects.create(
                id_psicologo=self.psicologo_base,
                id_idioma=idioma,
                id_estado=self.estado_activo,
            )

    def test_main_lists_paginate_by_ten(self):
        self.create_psicologos(12)
        self.create_pacientes(12)
        self.create_solicitudes(12)

        self.assert_paginated(reverse("usuario:psicologo_list"), "psicologos", second_page_count=3)
        self.assert_paginated(reverse("usuario:paciente_list"), "pacientes")
        self.assert_paginated(reverse("usuario:psicologo_pendiente_list"), "solicitudes")

    def test_psicologo_related_lists_paginate_by_ten(self):
        self.create_oficinas(12)
        self.create_metodos_pago(12)
        self.create_ramas_profesionales(12)
        self.create_idiomas(12)

        self.assert_paginated(reverse("usuario:psicologo_oficina_list"), "oficinas")
        self.assert_paginated(reverse("usuario:psicologo_metodo_pago_list"), "metodos_pago")
        self.assert_paginated(reverse("usuario:psicologo_rama_list"), "ramas", second_page_count=3)
        self.assert_paginated(reverse("usuario:psicologo_idioma_list"), "idiomas")
