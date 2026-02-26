import sqlite3

ranges = [
    ("Free Chlorine (ppm)", 1.0, 3.0, 0.10),
    ("Combined Chlorine (ppm)", 0.0, 0.2, 0.10),
    ("Total Chlorine (ppm)", 1.0, 3.2, 0.10),
    ("Salt Level (ppm)", 4000, 6000, 0.10),
    ("Alkalinity (ppm)", 80, 120, 0.10),
    ("pH", 7.2, 7.8, 0.10),
    ("Sunscreen (Stabiliser) (ppm)", 30, 50, 0.10),
    ("Total Hardness (ppm)", 150, 250, 0.10),
    ("Phosphates (ppm)", 0, 0.2, 0.20),
    ("Copper Total (ppm)", 0, 0.2, 0.10),
]

conn = sqlite3.connect("home_maintenance.db")
cur = conn.cursor()

cur.executemany("""
INSERT OR REPLACE INTO desired_ranges (item_name, low_value, high_value, factor_warn)
VALUES (?, ?, ?, ?)
""", ranges)

conn.commit()
conn.close()

print("Desired ranges inserted.")
