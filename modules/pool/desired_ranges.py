import sqlite3
from typing import Dict


class DesiredRanges:
    """
    Loads and manages desired ranges for pool test parameters.
    Backed by a SQLite table: desired_ranges(item_name, low_value, high_value, factor_warn)
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.ranges = {}  # item_name → {low, high, factor_warn}

    # ------------------------------------------------------------
    # Load all ranges from SQLite
    # ------------------------------------------------------------
    def load(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT item_name, low_value, high_value, factor_warn
            FROM desired_ranges
        """)

        rows = cur.fetchall()
        conn.close()

        self.ranges = {
            item: {
                "low": low,
                "high": high,
                "factor_warn": fw
            }
            for (item, low, high, fw) in rows
        }

        return self.ranges

    # ------------------------------------------------------------
    # Get range for a specific item
    # ------------------------------------------------------------
    def get(self, item_name: str):
        return self.ranges.get(item_name)

    # ------------------------------------------------------------
    # For debugging / UI
    # ------------------------------------------------------------
    def __repr__(self):
        return f"DesiredRanges({len(self.ranges)} items)"
