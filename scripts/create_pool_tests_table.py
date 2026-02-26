import sqlite3

conn = sqlite3.connect("home_maintenance.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS pool_tests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    test_date TEXT NOT NULL,

    free_chlorine REAL NOT NULL,
    combined_chlorine REAL NOT NULL,
    total_chlorine REAL NOT NULL,
    salt_level REAL NOT NULL,
    alkalinity REAL NOT NULL,
    ph REAL NOT NULL,
    sunscreen REAL NOT NULL,
    hardness REAL NOT NULL,
    phosphates REAL NOT NULL,
    copper REAL NOT NULL,

    clarity_notes TEXT,
    actions_taken TEXT,

    next_test_date TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Pool Tests table created.")
