import unittest
import pandas as pd
from django.test import TestCase, Client
from django.urls import reverse
from core.utils import build_network_data, run_match

class AdvancedFeaturesTest(TestCase):
    def setUp(self):
        self.df = pd.DataFrame({
            'doctor_name': ['Dr. Smith', 'Dr. Jones', 'Dr. Smith'],
            'patient_id': ['P1', 'P1', 'P2'],
            'patient_name': ['Alice', 'Alice', 'Bob'],
            '_rama': ['P1', 'P1', 'P2'],
            '_name': ['Alice', 'Alice', 'Bob'],
            '_date': pd.to_datetime(['2024-01-01', '2024-01-05', '2024-01-10'])
        })

    def test_network_data(self):
        net_data = build_network_data(self.df)
        self.assertTrue(len(net_data['nodes']) >= 4) # 2 doctors + 2 patients
        self.assertEqual(len(net_data['edges']), 3)

    def test_fraud_match(self):
        fac_df = pd.DataFrame({
            '_rama': ['P1'],
            '_name': ['Alice'],
            '_date': pd.to_datetime(['2024-01-01']),
            '_source': ['Hospital A']
        })
        # Mocking necessary columns for ph_work
        ph_work = self.df.copy()
        ph_work["_vou"] = ""
        ph_work["_ins"] = 100
        ph_work["_tot"] = 100

        res = run_match(ph_work, fac_df)
        # P1 on 2024-01-01 should be MATCHED
        # P1 on 2024-01-05 should be MATCHED (within 7 days)
        # P2 on 2024-01-10 should be NO_RECORD
        matched = res[res['status'] == 'MATCHED']
        self.assertEqual(len(matched), 2)
        no_record = res[res['status'] == 'NO_RECORD']
        self.assertEqual(len(no_record), 1)

if __name__ == '__main__':
    unittest.main()
