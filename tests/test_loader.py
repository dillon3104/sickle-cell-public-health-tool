import unittest
from pathlib import Path

from src.loader import preview_header, load_records


class TestLoader(unittest.TestCase):
    def setUp(self):
        self.sample_path = Path("tests/sample_scd.csv")

    def test_preview_header(self):
        header = preview_header(self.sample_path)
        self.assertIn("location_name", header)
        self.assertIn("year_id", header)
        self.assertIn("val", header)

    def test_load_records_limit(self):
        records = load_records(self.sample_path, limit=2)
        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].location, "Testland")
        self.assertEqual(records[0].year, 2020)
        self.assertEqual(records[0].measure, "Prevalence")
