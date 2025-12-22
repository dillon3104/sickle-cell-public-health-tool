import unittest
import sqlite3
from pathlib import Path

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
