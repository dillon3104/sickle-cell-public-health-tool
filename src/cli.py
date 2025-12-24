# src/cli.py
from __future__ import annotations

from pathlib import Path

from src import db
from src.loader import iter_records
from src import analysis
from src import visualise
from src import exporter



DATASET_DEFAULT_PATH = Path("data/raw/sickle_cell_gbd.CSV")


def _auto_cause_or_prompt(conn) -> str:
    causes = analysis.get_distinct_values(conn, "cause")
    if len(causes) == 1:
        # Only one cause in the dataset: pick automatically
        return causes[0]
    return _prompt_choice("Pick cause", causes)


def _prompt_choice(title: str, options: list[str], max_show: int = 30) -> str:
    """
    Show numbered options, let the user pick by number (or type exact text).
    """
    print("\n" + title)
    print("-" * len(title))

    if not options:
        raise ValueError("No options available (database may be empty).")

    show = options[:max_show]
    for i, opt in enumerate(show, start=1):
        print(f"{i}. {opt}")

    if len(options) > max_show:
        print(f"... ({len(options) - max_show} more not shown)")

    while True:
        choice = input("Enter number or exact text: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(show):
                return show[idx]
            print("Invalid number. Try again.")
        else:
            # exact match
            if choice in options:
                return choice
            # case-insensitive match
            lowered = {o.lower(): o for o in options}
            if choice.lower() in lowered:
                return lowered[choice.lower()]
            print("Not recognised. Try again.")


def _prompt_int(prompt: str) -> int:
    while True:
        s = input(prompt).strip()
        try:
            return int(s)
        except ValueError:
            print("Please enter a whole number.")


def load_dataset(conn) -> None:
    path = input(f"CSV path (Enter for default: {DATASET_DEFAULT_PATH}): ").strip()
    csv_path = Path(path) if path else DATASET_DEFAULT_PATH

    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    print("Initialising database...")
    db.init_db(conn)

    print(f"Loading CSV into SQLite (streaming): {csv_path}")
    attempted = db.insert_many(conn, iter_records(csv_path))
    total = db.row_count(conn)

    print(f"Attempted inserts: {attempted}")
    print(f"Rows currently in DB: {total}")


def menu() -> None:
    conn = db.connect()
    db.init_db(conn)

    while True:
        print("\nSickle Cell Public Health Data Tool")
        print("----------------------------------")
        print("1. Load dataset from CSV into database")
        print("2. List values (locations/measures/metrics/sex/age groups/years/causes)")
        print("3. Trend for a location (time series)")
        print("4. Summary stats (across locations)")
        print("5. Compare locations for a given year (top N)")
        print("6. Exit")

        choice = input("Choose an option: ").strip()

        try:
            if choice == "1":
                load_dataset(conn)

            elif choice == "2":
                col = _prompt_choice(
                    "Which field do you want to list?",
                    ["location", "measure", "metric", "sex", "age_group", "year", "cause"],
                    max_show=7,
                )
                vals = analysis.get_distinct_values(conn, col)
                print(f"\nDistinct {col} values (showing up to 50):")
                for v in vals[:50]:
                    print(f"- {v}")
                if len(vals) > 50:
                    print(f"... ({len(vals) - 50} more)")

            elif choice == "3":
                # Trend
                locations = analysis.get_distinct_values(conn, "location")
                measures = analysis.get_distinct_values(conn, "measure")
                metrics = analysis.get_distinct_values(conn, "metric")
                sexes = analysis.get_distinct_values(conn, "sex")
                ages = analysis.get_distinct_values(conn, "age_group")

                location = _prompt_choice("Pick a location", locations)
                measure = _prompt_choice("Pick a measure", measures)
                metric = _prompt_choice("Pick a metric", metrics)
                sex = _prompt_choice("Pick sex", sexes)
                age = _prompt_choice("Pick age group", ages)
                cause = _auto_cause_or_prompt(conn)

                series = analysis.get_trend(conn, location, measure, metric, sex=sex, age_group=age, cause=cause)
                if not series:
                    print("No data found for that selection.")
                else:
                    print("\nYear -> Value")
                    for y, v in series:
                        print(f"{y}: {v}")

                    years = [y for y, _ in series]
                    vals = [v for _, v in series]

                    title = f"Trend: {measure} ({metric}) | {location} | {sex} | {age}"
                    save = input("Save plot to file? (y/n): ").strip().lower() == "y"
                    save_path = None
                    if save:
                        safe_loc = location.replace("/", "-").replace("\\", "-")
                        safe_meas = measure.replace("/", "-").replace("\\", "-")
                        safe_met = metric.replace("/", "-").replace("\\", "-")
                        save_path = f"outputs/trend_{safe_loc}_{safe_meas}_{safe_met}.png"

                    visualise.plot_trend(
                        years=years,
                        values=vals,
                        title=title,
                        ylabel=metric,
                        save_path=save_path,
                    )

                    export_csv = input("Export trend results to CSV? (y/n): ").strip().lower() == "y"
                    if export_csv:
                        out_path = exporter.export_trend_csv(
                            rows=series,
                            out_dir="outputs",
                            location=location,
                            measure=measure,
                            metric=metric,
                            sex=sex,
                            age_group=age,
                            cause=cause,
                        )
                        print(f"Saved CSV to: {out_path}")



            elif choice == "4":
                # Summary stats
                measures = analysis.get_distinct_values(conn, "measure")
                metrics = analysis.get_distinct_values(conn, "metric")
                sexes = analysis.get_distinct_values(conn, "sex")
                ages = analysis.get_distinct_values(conn, "age_group")

                measure = _prompt_choice("Pick a measure", measures)
                metric = _prompt_choice("Pick a metric", metrics)
                sex = _prompt_choice("Pick sex", sexes)
                age = _prompt_choice("Pick age group", ages)
                cause = _auto_cause_or_prompt(conn)

                year_str = input("Year (blank = all years): ").strip()
                year = int(year_str) if year_str else None

                stats = analysis.summary_stats(conn, measure, metric, year=year, sex=sex, age_group=age, cause=cause)
                print("\nSummary stats (across locations)")
                print("--------------------------------")
                print(f"Count (n): {stats['n']}")
                print(f"Min: {stats['min']}")
                print(f"Mean: {stats['mean']}")
                print(f"Max: {stats['max']}")
                print(f"Filters: {stats['filters']}")

            elif choice == "5":
                # Compare
                measures = analysis.get_distinct_values(conn, "measure")
                metrics = analysis.get_distinct_values(conn, "metric")
                sexes = analysis.get_distinct_values(conn, "sex")
                ages = analysis.get_distinct_values(conn, "age_group")

                measure = _prompt_choice("Pick a measure", measures)
                metric = _prompt_choice("Pick a metric", metrics)
                year = _prompt_int("Year (e.g., 2021): ")
                sex = _prompt_choice("Pick sex", sexes)
                age = _prompt_choice("Pick age group", ages)
                cause = _auto_cause_or_prompt(conn)

                top_n = _prompt_int("How many locations to show (e.g., 10): ")
                order = _prompt_choice("Order", ["desc", "asc"], max_show=2)

                rows = analysis.compare_locations(
                    conn, measure, metric, year, sex=sex, age_group=age, cause=cause, top_n=top_n, order=order
                )
                if not rows:
                    print("No data found.")
                else:
                    print("\nLocation -> Value")
                    print("-----------------")
                    for loc, val in rows:
                        print(f"{loc}: {val}")

                    labels = [loc for loc, _ in rows]
                    vals = [val for _, val in rows]

                    title = f"Top {top_n}: {measure} ({metric}) | {year} | {sex} | {age}"
                    save = input("Save plot to file? (y/n): ").strip().lower() == "y"
                    save_path = None
                    if save:
                        safe_meas = measure.replace("/", "-").replace("\\", "-")
                        safe_met = metric.replace("/", "-").replace("\\", "-")
                        save_path = f"outputs/compare_{year}_{safe_meas}_{safe_met}.png"

                    visualise.plot_bar_comparison(
                        labels=labels,
                        values=vals,
                        title=title,
                        ylabel=metric,
                        save_path=save_path,
                        max_labels=min(25, top_n),
                    )

                    export_csv = input("Export comparison results to CSV? (y/n): ").strip().lower() == "y"
                    if export_csv:
                        out_path = exporter.export_compare_csv(
                            rows=rows,
                            out_dir="outputs",
                            year=year,
                            measure=measure,
                            metric=metric,
                            sex=sex,
                            age_group=age,
                            cause=cause,
                            order=order,
                        )
                        print(f"Saved CSV to: {out_path}")


            elif choice == "6":
                print("Goodbye!")
                break

            else:
                print("Invalid option. Try 1–6.")

        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    menu()
