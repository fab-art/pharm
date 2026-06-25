import unittest
import base64
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile

class InteractiveFlowTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.csv_content = "paper code,dispensing date,patient name,rama number,total cost\nV001,2024-01-01,John Doe,R123,100.0\nV002,2024-01-02,John Doe,R123,150.0"
        self.test_file = SimpleUploadedFile("test.csv", self.csv_content.encode('utf-8'), content_type="text/csv")

    def test_full_flow(self):
        # 1. Upload
        response = self.client.post(reverse('core:upload'), {'file': self.test_file, 'rapid_days': 7}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Validate Mapping")

        # 2. Mapping
        # In the real template, fields are map_OriginalName
        response = self.client.post(reverse('core:mapping'), {
            'map_paper_code': 'voucher_id',
            'map_dispensing_date': 'visit_date',
            'map_patient_name': 'patient_name',
            'map_rama_number': 'patient_id',
            'map_total_cost': 'amount'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Analytics Dashboard")

        # 3. Dashboard content
        self.assertContains(response, "Total Records")
        self.assertContains(response, "2") # Total rows
        self.assertContains(response, "John Doe")

        # 4. Export
        response = self.client.get(reverse('core:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn(b"John Doe", response.content)

if __name__ == '__main__':
    unittest.main()
