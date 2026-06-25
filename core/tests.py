from django.test import TestCase
from django.urls import reverse

class IndexViewTest(TestCase):
    def test_index_view_status_code(self):
        response = self.client.get(reverse('core:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PharmaScan")
        self.assertContains(response, "System Dashboard")

    def test_cyber_dark_aesthetic(self):
        response = self.client.get(reverse('core:index'))
        # Check for specified hex colors
        self.assertContains(response, "#080c10") # background
        self.assertContains(response, "#0d1117") # sidebar/card
        self.assertContains(response, "#1e2a38") # border
        self.assertContains(response, "#00e5a0") # accent green
        self.assertContains(response, "#0ea5e9") # accent blue
