import sqlite3
import sys


DB_PATH = "home_maintenance.db"


def fail(msg: str):
    print(f"FAIL: {msg}")
    return False


def ok(msg: str):
    print(f"OK: {msg}")
    return True


def main() -> int:
    all_ok = True
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("PRAGMA integrity_check")
    integrity = cur.fetchone()[0]
    if integrity == "ok":
        ok("SQLite integrity_check passed")
    else:
        all_ok = fail(f"integrity_check returned: {integrity}") and all_ok

    for table in ("rainfall", "settings"):
        cur.execute(
            "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?",
            (table,),
        )
        exists = cur.fetchone()[0] == 1
        if exists:
            ok(f"table exists: {table}")
        else:
            all_ok = fail(f"missing table: {table}") and all_ok

    cur.execute("SELECT COUNT(*) FROM rainfall WHERE watered NOT IN ('Yes','No') OR watered IS NULL")
    bad_watered = cur.fetchone()[0]
    if bad_watered == 0:
        ok("watered domain valid")
    else:
        all_ok = fail(f"invalid watered rows: {bad_watered}") and all_ok

    cur.execute("SELECT COUNT(*) FROM rainfall WHERE rain_mm < 0 OR bom_mm < 0")
    bad_mm = cur.fetchone()[0]
    if bad_mm == 0:
        ok("rain/bom values non-negative")
    else:
        all_ok = fail(f"negative rainfall rows: {bad_mm}") and all_ok

    cur.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT date, COUNT(*) c
            FROM rainfall
            GROUP BY date
            HAVING c > 1
        )
    """)
    dup_dates = cur.fetchone()[0]
    if dup_dates == 0:
        ok("no duplicate rainfall dates")
    else:
        all_ok = fail(f"duplicate date groups: {dup_dates}") and all_ok

    for key in ("threshold_mm", "period_days"):
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        if row is None:
            all_ok = fail(f"missing settings key: {key}") and all_ok
            continue
        try:
            if key == "threshold_mm":
                float(row[0])
            else:
                iv = int(row[0])
                if iv <= 0:
                    raise ValueError("period_days must be > 0")
        except Exception:
            all_ok = fail(f"invalid settings value for {key}: {row[0]}") and all_ok
        else:
            ok(f"settings key valid: {key}={row[0]}")

    conn.close()
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
