import unittest
from pathlib import Path
import tempfile
from src.loader import iter_records, preview_header
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


    def test_iter_records_skips_row_with_missing_year(self):
        csv_text = (
            "measure_id,measure_name,location_id,location_name,sex_id,sex_name,age_group_id,age_group_name,"
            "cause_id,cause_name,metric_id,metric_name,year_id,val,upper,lower\n"
            "1,Prevalence,100,Testland,3,Both,22,All Ages,999,Sickle cell disorders,1,Rate,,10.0,11.0,9.0\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tf:
            tf.write(csv_text)
            tmp = Path(tf.name)

        recs = list(iter_records(tmp))
        self.assertEqual(recs, [])  # skipped because year missing

    def test_iter_records_handles_float_year_string(self):
        csv_text = (
            "measure_id,measure_name,location_id,location_name,sex_id,sex_name,age_group_id,age_group_name,"
            "cause_id,cause_name,metric_id,metric_name,year_id,val,upper,lower\n"
            "1,Prevalence,100,Testland,3,Both,22,All Ages,999,Sickle cell disorders,1,Rate,2021.0,10.0,11.0,9.0\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tf:
            tf.write(csv_text)
            tmp = Path(tf.name)

        recs = list(iter_records(tmp))
        self.assertEqual(recs[0].year, 2021)

    def test_iter_records_works_without_upper_lower_columns(self):
        # upper/lower optional branch
        csv_text = (
            "measure_id,measure_name,location_id,location_name,sex_id,sex_name,age_group_id,age_group_name,"
            "cause_id,cause_name,metric_id,metric_name,year_id,val\n"
            "1,Prevalence,100,Testland,3,Both,22,All Ages,999,Sickle cell disorders,1,Rate,2021,10.0\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tf:
            tf.write(csv_text)
            tmp = Path(tf.name)

        recs = list(iter_records(tmp))
        self.assertEqual(len(recs), 1)
        self.assertIsNone(recs[0].upper)
        self.assertIsNone(recs[0].lower)