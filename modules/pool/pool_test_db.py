import sqlite3
from typing import List, Optional
from datetime import date

from .pool_test import PoolTest


class PoolTestDB:
    """
    Handles saving, loading, listing, updating, and deleting PoolTest records
    from the SQLite database.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------
    # Insert a new PoolTest into the database
    # ------------------------------------------------------------
    def insert(self, test: PoolTest) -> int:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO pool_tests (
                test_date,
                free_chlorine,
                combined_chlorine,
                total_chlorine,
                salt_level,
                alkalinity,
                ph,
                sunscreen,
                hardness,
                phosphates,
                copper,
                clarity_notes,
                actions_taken,
                next_test_date
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            test.test_date.isoformat(),
            test.free_chlorine,
            test.combined_chlorine,
            test.total_chlorine,
            test.salt_level,
            test.alkalinity,
            test.ph,
            test.sunscreen,
            test.hardness,
            test.phosphates,
            test.copper,
            test.clarity_notes,
            test.actions_taken,
            test.next_test_date.isoformat()
        ))

        conn.commit()
        new_id = cur.lastrowid
        conn.close()

        return new_id

    # ------------------------------------------------------------
    # Update an existing PoolTest
    # ------------------------------------------------------------
    def update(self, test_id: int, test: PoolTest):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            UPDATE pool_tests
            SET
                test_date = ?,
                free_chlorine = ?,
                combined_chlorine = ?,
                total_chlorine = ?,
                salt_level = ?,
                alkalinity = ?,
                ph = ?,
                sunscreen = ?,
                hardness = ?,
                phosphates = ?,
                copper = ?,
                clarity_notes = ?,
                actions_taken = ?,
                next_test_date = ?
            WHERE id = ?
        """, (
            test.test_date.isoformat(),
            test.free_chlorine,
            test.combined_chlorine,
            test.total_chlorine,
            test.salt_level,
            test.alkalinity,
            test.ph,
            test.sunscreen,
            test.hardness,
            test.phosphates,
            test.copper,
            test.clarity_notes,
            test.actions_taken,
            test.next_test_date.isoformat(),
            test_id
        ))

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # Load a single PoolTest by ID
    # ------------------------------------------------------------
    def load(self, test_id: int) -> Optional[PoolTest]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                test_date,
                free_chlorine,
                combined_chlorine,
                total_chlorine,
                salt_level,
                alkalinity,
                ph,
                sunscreen,
                hardness,
                phosphates,
                copper,
                clarity_notes,
                actions_taken,
                next_test_date
            FROM pool_tests
            WHERE id = ?
        """, (test_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        (
            _id,
            test_date,
            free_chlorine,
            combined_chlorine,
            total_chlorine,
            salt_level,
            alkalinity,
            ph,
            sunscreen,
            hardness,
            phosphates,
            copper,
            clarity_notes,
            actions_taken,
            next_test_date
        ) = row

        # IMPORTANT: include id=_id
        test = PoolTest(
            test_date=date.fromisoformat(test_date),
            free_chlorine=free_chlorine,
            combined_chlorine=combined_chlorine,
            total_chlorine=total_chlorine,
            salt_level=salt_level,
            alkalinity=alkalinity,
            ph=ph,
            sunscreen=sunscreen,
            hardness=hardness,
            phosphates=phosphates,
            copper=copper,
            clarity_notes=clarity_notes,
            actions_taken=actions_taken,
            id=_id
        )

        # Override next_test_date from DB
        test.next_test_date = date.fromisoformat(next_test_date)

        return test

    # ------------------------------------------------------------
    # List all PoolTests
    # ------------------------------------------------------------
    def list_all(self) -> List[PoolTest]:
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("""
            SELECT
                id,
                test_date,
                free_chlorine,
                combined_chlorine,
                total_chlorine,
                salt_level,
                alkalinity,
                ph,
                sunscreen,
                hardness,
                phosphates,
                copper,
                clarity_notes,
                actions_taken,
                next_test_date
            FROM pool_tests
            ORDER BY test_date DESC
        """)

        rows = cur.fetchall()
        conn.close()

        tests = []
        for row in rows:
            (
                _id,
                test_date,
                free_chlorine,
                combined_chlorine,
                total_chlorine,
                salt_level,
                alkalinity,
                ph,
                sunscreen,
                hardness,
                phosphates,
                copper,
                clarity_notes,
                actions_taken,
                next_test_date
            ) = row

            test = PoolTest(
                test_date=date.fromisoformat(test_date),
                free_chlorine=free_chlorine,
                combined_chlorine=combined_chlorine,
                total_chlorine=total_chlorine,
                salt_level=salt_level,
                alkalinity=alkalinity,
                ph=ph,
                sunscreen=sunscreen,
                hardness=hardness,
                phosphates=phosphates,
                copper=copper,
                clarity_notes=clarity_notes,
                actions_taken=actions_taken,
                id=_id,   # <-- ADD THIS
            )

            test.next_test_date = date.fromisoformat(next_test_date)
            tests.append(test)

        return tests

    # ------------------------------------------------------------
    # Delete a PoolTest by ID
    # ------------------------------------------------------------
    def delete(self, test_id: int):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()

        cur.execute("DELETE FROM pool_tests WHERE id = ?", (test_id,))
        conn.commit()
        conn.close()
