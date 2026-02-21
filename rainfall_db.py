import sqlite3
from datetime import date, datetime, timedelta
from typing import List, Optional


DATE_FMT = "%Y-%m-%d"


class RainfallRecord:
    """
    A simple container for rainfall data.
    Mirrors the old CSV structure but stored in SQLite.
    """

    def __init__(
        self,
        date_obj: date,
        rain_mm: Optional[float],
        bom_mm: Optional[float],
        notes: str,
        watered: str,
        moisture: float,
        record_id: Optional[int] = None,
    ):
        self.id = record_id
        self.date = date_obj
        self.rain_mm = rain_mm
        self.bom_mm = bom_mm
        self.notes = notes
        self.watered = watered
        self.moisture = moisture

    def effective_mm(self) -> Optional[float]:
        """Return effective rainfall (Rain_mm first, then BOM_mm)."""
        if self.rain_mm is not None and self.rain_mm >= 0:
            return self.rain_mm
        if self.bom_mm is not None and self.bom_mm >= 0:
            return self.bom_mm
        return None


class RainfallDB:
    """
    Handles all rainfall storage and retrieval.
    Replaces CSV and JSON data layers.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def _connect(self):
        return sqlite3.connect(self.db_path)

    # ------------------------------------------------------------
    # Insert
    # ------------------------------------------------------------
    def insert(self, rec: RainfallRecord) -> int:
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO rainfall (
                date, rain_mm, bom_mm, notes, watered, moisture
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            rec.date.isoformat(),
            rec.rain_mm,
            rec.bom_mm,
            rec.notes,
            rec.watered,
            rec.moisture,
        ))

        conn.commit()
        new_id = cur.lastrowid
        conn.close()
        return new_id

    # ------------------------------------------------------------
    # Update
    # ------------------------------------------------------------
    def update(self, rec_id: int, rec: RainfallRecord):
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            UPDATE rainfall
            SET date=?, rain_mm=?, bom_mm=?, notes=?, watered=?, moisture=?
            WHERE id=?
        """, (
            rec.date.isoformat(),
            rec.rain_mm,
            rec.bom_mm,
            rec.notes,
            rec.watered,
            rec.moisture,
            rec_id,
        ))

        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------
    def delete(self, rec_id: int):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM rainfall WHERE id=?", (rec_id,))
        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # Load single record
    # ------------------------------------------------------------
    def load(self, rec_id: int) -> Optional[RainfallRecord]:
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, date, rain_mm, bom_mm, notes, watered, moisture
            FROM rainfall
            WHERE id=?
        """, (rec_id,))

        row = cur.fetchone()
        conn.close()

        if not row:
            return None

        return RainfallRecord(
            date_obj=date.fromisoformat(row[1]),
            rain_mm=row[2],
            bom_mm=row[3],
            notes=row[4],
            watered=row[5],
            moisture=row[6],
            record_id=row[0],
        )

    # ------------------------------------------------------------
    # List all records (sorted by date)
    # ------------------------------------------------------------
    def list_all(self) -> List[RainfallRecord]:
        conn = self._connect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, date, rain_mm, bom_mm, notes, watered, moisture
            FROM rainfall
            ORDER BY date ASC
        """)

        rows = cur.fetchall()
        conn.close()

        records = []
        for row in rows:
            records.append(
                RainfallRecord(
                    date_obj=date.fromisoformat(row[1]),
                    rain_mm=row[2],
                    bom_mm=row[3],
                    notes=row[4],
                    watered=row[5],
                    moisture=row[6],
                    record_id=row[0],
                )
            )
        return records

    # ------------------------------------------------------------
    # Missing days detection
    # ------------------------------------------------------------
    def compute_missing_dates(self):
        records = self.list_all()
        if not records:
            return []

        dates = sorted(r.date for r in records)
        all_dates = []
        d = dates[0]
        while d <= dates[-1]:
            all_dates.append(d)
            d += timedelta(days=1)

        existing = set(dates)
        return [d for d in all_dates if d not in existing]

    # ------------------------------------------------------------
    # Last rainfall date
    # ------------------------------------------------------------
    def last_rain_date(self):
        records = self.list_all()
        last = None
        for r in records:
            eff = r.effective_mm()
            if eff is not None and eff > 0:
                if last is None or r.date > last:
                    last = r.date
        return last

    # ------------------------------------------------------------
    # Last watering date
    # ------------------------------------------------------------
    def last_watering_date(self):
        records = self.list_all()
        last = None
        for r in records:
            if r.watered == "Yes":
                if last is None or r.date > last:
                    last = r.date
        return last
