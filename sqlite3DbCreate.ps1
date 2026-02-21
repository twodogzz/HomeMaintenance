import sqlite3

conn = sqlite3.connect("home_maintenance.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS desired_ranges (
    item_name      TEXT PRIMARY KEY,
    low_value      REAL NOT NULL,
    high_value     REAL NOT NULL,
    factor_warn    REAL NOT NULL
)
""")

conn.commit()
conn.close()

print("Database initialised.")