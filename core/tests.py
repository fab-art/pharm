import unittest
import pandas as pd
import io
from core.utils import load_and_process, hbar_chart_buf, time_series_chart_buf, rapid_histogram_buf

class TestUtils(unittest.TestCase):
    def test_load_and_process_csv(self):
        csv_content = "paper code,dispensing date,patient name,rama number,total cost\nV001,2024-01-01,John Doe,R123,100.0\nV002,2024-01-02,John Doe,R123,150.0"
        file_bytes = csv_content.encode('utf-8')
        df, renamed, s, repeat_groups, repeat_detail, rapid = load_and_process(file_bytes, "test.csv", 7)

        self.assertEqual(len(df), 2)
        self.assertIn('visit_date', df.columns)
        self.assertIn('patient_id', df.columns)
        self.assertEqual(s['total_rows'], 2)
        self.assertEqual(len(rapid), 1) # V001 to V002 is 1 day apart
        self.assertEqual(rapid[0]['days_apart'], 1)

    def test_charts(self):
        # Just check if they return a buffer
        labels = ['A', 'B']
        values = [10, 20]
        buf = hbar_chart_buf(labels, values, "#00e5a0", "Test", "X")
        self.assertIsInstance(buf, io.BytesIO)

        df = pd.DataFrame({
            'visit_date': pd.to_datetime(['2024-01-01', '2024-02-01'])
        })
        buf = time_series_chart_buf(df)
        self.assertIsInstance(buf, io.BytesIO)

        rapid = [{'days_apart': 1}, {'days_apart': 5}]
        buf = rapid_histogram_buf(rapid)
        self.assertIsInstance(buf, io.BytesIO)

if __name__ == '__main__':
    unittest.main()
