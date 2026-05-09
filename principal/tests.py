from django.test import TestCase
from django.urls import reverse


class HomePageTests(TestCase):
    def test_home_page_shows_services_and_registration_links(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sistema Psicologia")
        self.assertContains(response, "Servicios")
        self.assertContains(response, reverse("usuario:paciente_create"))
        self.assertContains(response, reverse("usuario:psicologo_create"))
