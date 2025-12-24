import unittest
import csv
import tempfile
from pathlib import Path

from src import exporter


class TestExporter(unittest.TestCase):
    def test_export_trend_csv_creates_file_and_contents(self):
        series = [(2020, 10.0), (2021, 12.0)]

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)

            # Use unsafe characters to ensure filename sanitisation works
            out_path = exporter.export_trend_csv(
                rows=series,
                out_dir=out_dir,
                location="Lat/veria",
                measure="Prev:alence",
                metric="Rate",
                sex="Both",
                age_group="All Ages",
                cause="Sickle cell disorders",
            )

            self.assertTrue(out_path.exists())

            # Read CSV and verify key rows exist
            with out_path.open("r", newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            # Metadata rows
            self.assertEqual(rows[0], ["cause", "location", "measure", "metric", "sex", "age_group"])
            self.assertEqual(rows[1][0], "Sickle cell disorders")
            self.assertEqual(rows[1][1], "Lat/veria")  # original value preserved in content

            # Data header then data rows should appear after a blank line
            self.assertIn(["year", "value"], rows)
            self.assertIn(["2020", "10.0"], rows)
            self.assertIn(["2021", "12.0"], rows)

    def test_export_compare_csv_creates_file_and_contents(self):
        rows_in = [("Jarhanpur", 12.0), ("Boravia", 20.0)]

        with tempfile.TemporaryDirectory() as td:
            out_dir = Path(td)

            out_path = exporter.export_compare_csv(
                rows=rows_in,
                out_dir=out_dir,
                year=2021,
                measure="Prevalence",
                metric="Rate",
                sex="Both",
                age_group="All Ages",
                cause="Sickle cell disorders",
                order="desc",
            )

            self.assertTrue(out_path.exists())

            with out_path.open("r", newline="", encoding="utf-8") as f:
                rows = list(csv.reader(f))

            self.assertEqual(rows[0], ["cause", "year", "measure", "metric", "sex", "age_group", "order"])
            self.assertEqual(rows[1], ["Sickle cell disorders", "2021", "Prevalence", "Rate", "Both", "All Ages", "desc"])

            self.assertIn(["location", "value"], rows)
            self.assertIn(["Jarhanpur", "12.0"], rows)
            self.assertIn(["Boravia", "20.0"], rows)
