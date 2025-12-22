import unittest
import sqlite3
from pathlib import Path

from src import db, analysis
from src.loader import iter_records


class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        db.init_db(self.conn)
        sample_path = Path("tests/sample_scd.csv")
        db.insert_many(self.conn, iter_records(sample_path), batch_size=10)

    def tearDown(self):
        self.conn.close()

    def test_get_trend(self):
        series = analysis.get_trend(
            self.conn,
            location="Testland",
            measure="Prevalence",
            metric="Rate",
            sex="Both",
            age_group="All Ages",
            cause="Sickle cell disorders",
        )
        self.assertEqual(series, [(2020, 10.0), (2021, 12.0)])

    def test_summary_stats_year(self):
        stats = analysis.summary_stats(
            self.conn,
            measure="Prevalence",
            metric="Rate",
            year=2021,
            sex="Both",
            age_group="All Ages",
            cause="Sickle cell disorders",
        )
        # For 2021 prevalence rate we have Testland=12, Examplestan=20 -> mean 16
        self.assertEqual(stats["n"], 2)
        self.assertAlmostEqual(stats["min"], 12.0)
        self.assertAlmostEqual(stats["max"], 20.0)
        self.assertAlmostEqual(stats["mean"], 16.0)
