import csv
import json
import os
import sqlite3
from datetime import datetime

DATE_FMT = "%Y-%m-%d"

DB_PATH = "home_maintenance.db"
SETTINGS_JSON = "settings.json"
DEFAULT_RAIN_CSV = r"E:\OneDrive\MyApps\Rainfall_Logger\rain_data.csv"


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
        watered TEXT NOT NULL DEFAULT 'No',
        moisture REAL
    )
    """)

    cur.execute("""
        UPDATE rainfall
        SET watered='No'
        WHERE watered IS NULL OR watered NOT IN ('Yes', 'No')
    """)
    cur.execute("""
        DELETE FROM rainfall
        WHERE id NOT IN (
            SELECT MAX(id) FROM rainfall GROUP BY date
        )
    """)
    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ux_rainfall_date
        ON rainfall(date)
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


def prompt_migrate_legacy_settings() -> bool:
    if not os.path.exists(SETTINGS_JSON):
        return False

    response = input(
        f"Import legacy settings from {SETTINGS_JSON}? [y/N]: "
    ).strip().lower()
    return response in ("y", "yes")


# ------------------------------------------------------------
# Import rain_data.csv → rainfall table
# ------------------------------------------------------------
def migrate_rainfall(csv_path: str):
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path} — skipping rainfall migration.")
        return

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    upserted = 0
    skipped = 0
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            d_str = row.get("Date", "").strip()
            try:
                d_obj = datetime.strptime(d_str, DATE_FMT).date()
            except Exception:
                print(f"Skipping invalid date row: {row}")
                skipped += 1
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
            watered = "Yes" if row.get("Watered", "No") == "Yes" else "No"

            cur.execute("""
                INSERT INTO rainfall (date, rain_mm, bom_mm, notes, watered, moisture)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(date) DO UPDATE SET
                    rain_mm=excluded.rain_mm,
                    bom_mm=excluded.bom_mm,
                    notes=excluded.notes,
                    watered=excluded.watered,
                    moisture=excluded.moisture
            """, (
                d_obj.isoformat(),
                rain_val,
                bom_val,
                notes,
                watered,
                moisture_val,
            ))
            upserted += 1

    migrated_at = datetime.now().isoformat(timespec="seconds")
    cur.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, ("rainfall_migration_source_csv", csv_path))
    cur.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, ("rainfall_migrated_at", migrated_at))
    cur.execute("""
        INSERT INTO settings (key, value)
        VALUES (?, ?)
        ON CONFLICT(key) DO UPDATE SET value=excluded.value
    """, ("rainfall_migration_version", "2"))

    conn.commit()
    conn.close()

    print(f"Rainfall records upserted: {upserted}. Skipped: {skipped}.")


def prompt_rainfall_csv_path() -> str:
    while True:
        if os.path.exists(DEFAULT_RAIN_CSV):
            prompt = (
                f"Enter full path to rainfall CSV file "
                f"[Press Enter for default: {DEFAULT_RAIN_CSV}]: "
            )
        else:
            prompt = "Enter full path to rainfall CSV file: "

        csv_path = input(prompt).strip().strip('"')
        if not csv_path and os.path.exists(DEFAULT_RAIN_CSV):
            csv_path = DEFAULT_RAIN_CSV

        if not csv_path:
            print("No file provided. Rainfall migration cancelled.")
            return ""
        if not os.path.exists(csv_path):
            print("File does not exist. Please try again.")
            continue
        if not os.path.isfile(csv_path):
            print("Path is not a file. Please try again.")
            continue
        return csv_path


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():
    print("Starting rainfall migration...")

    ensure_tables()
    if prompt_migrate_legacy_settings():
        migrate_settings()
    else:
        print("Legacy settings import skipped.")
    csv_path = prompt_rainfall_csv_path()
    if csv_path:
        migrate_rainfall(csv_path)

    print("\nMigration complete.")
    print("Runtime now uses SQLite data only.")


if __name__ == "__main__":
    main()
