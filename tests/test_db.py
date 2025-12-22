import unittest
import sqlite3
from pathlib import Path
import tempfile

from src import db
from src.loader import iter_records


class TestDB(unittest.TestCase):
    def setUp(self):
        # In-memory DB = fast and doesn't create files
        self.conn = sqlite3.connect(":memory:")
        db.init_db(self.conn)
        self.sample_path = Path("tests/sample_scd.csv")

    def tearDown(self):
        self.conn.close()

    def test_insert_and_count(self):
        attempted = db.insert_many(self.conn, iter_records(self.sample_path), batch_size=2)
        self.assertGreater(attempted, 0)

        count = db.row_count(self.conn)
        self.assertEqual(count, 4)  # we inserted 4 rows in sample csv

    def test_list_measures(self):
        db.insert_many(self.conn, iter_records(self.sample_path), batch_size=10)
        measures = db.list_measures(self.conn)
        self.assertIn("Prevalence", measures)
        self.assertIn("Mortality", measures)


    def test_connect_creates_db_file_and_connects(self):
        with tempfile.TemporaryDirectory() as td:
            db_path = Path(td) / "temp.db"
            conn = db.connect(db_path)
            try:
                db.init_db(conn)
                self.assertTrue(db_path.exists())
            finally:
                conn.close()

    def test_clear_data_empties_table(self):
        db.insert_many(self.conn, iter_records(self.sample_path), batch_size=10)
        self.assertEqual(db.row_count(self.conn), 4)

        db.clear_data(self.conn)
        self.assertEqual(db.row_count(self.conn), 0)

    def test_list_locations_limit_branch(self):
        db.insert_many(self.conn, iter_records(self.sample_path), batch_size=10)
        locs = db.list_locations(self.conn, limit=1)
        self.assertEqual(len(locs), 1)

    def test_list_metrics_and_years(self):
        db.insert_many(self.conn, iter_records(self.sample_path), batch_size=10)
        metrics = db.list_metrics(self.conn)
        years = db.list_years(self.conn)
        self.assertIn("Rate", metrics)
        self.assertIn(2021, years)

    def test_list_locations_no_limit_branch(self):
        db.insert_many(self.conn, iter_records(self.sample_path), batch_size=10)
        locs = db.list_locations(self.conn)  # no limit -> else branch
        self.assertGreaterEqual(len(locs), 2)
        self.assertIn("Testland", locs)


