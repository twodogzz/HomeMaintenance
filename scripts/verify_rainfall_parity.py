import csv
import os
import sqlite3
import sys
from datetime import datetime


DATE_FMT = "%Y-%m-%d"
DB_PATH = "home_maintenance.db"
DEFAULT_RAIN_CSV = r"E:\OneDrive\MyApps\Rainfall_Logger\rain_data.csv"


def parse_float(val):
    raw = (val or "").strip()
    if raw == "":
        return None
    try:
        return float(raw)
    except Exception:
        return None


def normalize_csv_row(row):
    d = (row.get("Date") or "").strip()
    datetime.strptime(d, DATE_FMT)
    return (
        d,
        parse_float(row.get("Rain_mm")),
        parse_float(row.get("BOM_mm")),
        (row.get("Notes") or ""),
        "Yes" if (row.get("Watered") or "No") == "Yes" else "No",
        parse_float(row.get("Moisture")),
    )


def main() -> int:
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_RAIN_CSV
    if not os.path.exists(csv_path):
        print(f"FAIL: CSV not found: {csv_path}")
        return 1

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        csv_rows = {}
        skipped = 0
        for row in reader:
            try:
                n = normalize_csv_row(row)
            except Exception:
                skipped += 1
                continue
            csv_rows[n[0]] = n

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT date, rain_mm, bom_mm, notes, watered, moisture
        FROM rainfall
        ORDER BY date
    """)
    db_rows = {r[0]: r for r in cur.fetchall()}
    conn.close()

    csv_dates = set(csv_rows.keys())
    db_dates = set(db_rows.keys())
    only_csv = sorted(csv_dates - db_dates)
    only_db = sorted(db_dates - csv_dates)

    mismatches = []
    for d in sorted(csv_dates & db_dates):
        if csv_rows[d] != db_rows[d]:
            mismatches.append((d, csv_rows[d], db_rows[d]))

    print(f"CSV rows (valid unique dates): {len(csv_rows)}")
    print(f"DB rows: {len(db_rows)}")
    print(f"CSV rows skipped due to invalid date: {skipped}")
    print(f"Dates only in CSV: {len(only_csv)}")
    print(f"Dates only in DB: {len(only_db)}")
    print(f"Value mismatches: {len(mismatches)}")

    if only_csv:
        print("Sample only-in-CSV dates:", ", ".join(only_csv[:10]))
    if only_db:
        print("Sample only-in-DB dates:", ", ".join(only_db[:10]))
    if mismatches:
        print("Sample mismatch:")
        d, c, b = mismatches[0]
        print(" date:", d)
        print(" csv :", c)
        print(" db  :", b)

    return 0 if not only_csv and not only_db and not mismatches else 1


if __name__ == "__main__":
    sys.exit(main())
