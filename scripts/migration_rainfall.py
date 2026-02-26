import csv
import json
import os
import sqlite3
from datetime import datetime

DATE_FMT = "%Y-%m-%d"

DB_PATH = "home_maintenance.db"
SETTINGS_JSON = "settings.json"
RAIN_CSV = "rain_data.csv"


# ------------------------------------------------------------
# Ensure tables exist
# ------------------------------------------------------------
def ensure_tables():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Rainfall table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS rainfall (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        rain_mm REAL,
        bom_mm REAL,
        notes TEXT,
        watered TEXT,
        moisture REAL
    )
    """)

    # Settings table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------------------
# Import settings.json → settings table
# ------------------------------------------------------------
def migrate_settings():
    if not os.path.exists(SETTINGS_JSON):
        print("No settings.json found — skipping settings migration.")
        return

    with open(SETTINGS_JSON, "r", encoding="utf-8") as f:
        try:
            settings = json.load(f)
        except Exception:
            print("settings.json is invalid — skipping.")
            return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    for key, value in settings.items():
        cur.execute("""
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, str(value)))

    conn.commit()
    conn.close()

    print("Settings migrated.")


# ------------------------------------------------------------
# Import rain_data.csv → rainfall table
# ------------------------------------------------------------
def migrate_rainfall():
    if not os.path.exists(RAIN_CSV):
        print("No rain_data.csv found — skipping rainfall migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Clear existing rainfall rows (safe because migration is one-time)
    cur.execute("DELETE FROM rainfall")

    with open(RAIN_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            d_str = row.get("Date", "").strip()
            try:
                d_obj = datetime.strptime(d_str, DATE_FMT).date()
            except Exception:
                print(f"Skipping invalid date row: {row}")
                continue

            # Parse numeric fields safely
            def parse_float(val):
                try:
                    if val.strip() == "":
                        return None
                    return float(val)
                except Exception:
                    return None

            rain_val = parse_float(row.get("Rain_mm", ""))
            bom_val = parse_float(row.get("BOM_mm", ""))
            moisture_val = parse_float(row.get("Moisture", ""))

            notes = row.get("Notes", "")
            watered = row.get("Watered", "No")

            cur.execute("""
                INSERT INTO rainfall (date, rain_mm, bom_mm, notes, watered, moisture)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                d_obj.isoformat(),
                rain_val,
                bom_val,
                notes,
                watered,
                moisture_val,
            ))

    conn.commit()
    conn.close()

    print("Rainfall records migrated.")


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print("Starting rainfall migration...")

    ensure_tables()
    migrate_settings()
    migrate_rainfall()

    print("\nMigration complete.")
    print("You may now delete settings.json and rain_data.csv if you wish.")


if __name__ == "__main__":
    main()
