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

    def test_get_distinct_values_invalid_column_raises(self):
        with self.assertRaises(ValueError):
            analysis.get_distinct_values(self.conn, "not_a_column")

    def test_get_distinct_values_year_branch(self):
        years = analysis.get_distinct_values(self.conn, "year")
        self.assertIn("2021", years)

    def test_compare_locations_asc(self):
        rows = analysis.compare_locations(
            self.conn,
            measure="Prevalence",
            metric="Rate",
            year=2021,
            sex="Both",
            age_group="All Ages",
            cause="Sickle cell disorders",
            top_n=10,
            order="asc",
        )
        # Ascending: Testland (12) should appear before Examplestan (20)
        self.assertEqual(rows[0][0], "Testland")
        self.assertAlmostEqual(rows[0][1], 12.0)

    def test_compare_locations_without_cause(self):
        # cause omitted branch
        rows = analysis.compare_locations(
            self.conn,
            measure="Prevalence",
            metric="Rate",
            year=2021,
            sex="Both",
            age_group="All Ages",
            cause=None,
            top_n=10,
            order="desc",
        )
        self.assertTrue(len(rows) >= 1)

    def test_get_distinct_values_non_year_branch(self):
        locs = analysis.get_distinct_values(self.conn, "location")
        self.assertIn("Testland", locs)

    def test_compare_locations_invalid_order_hits_raise_line(self):
        with self.assertRaises(ValueError):
            analysis.compare_locations(
                self.conn,
                measure="Prevalence",
                metric="Rate",
                year=2021,
                order="invalid",
            )


    

