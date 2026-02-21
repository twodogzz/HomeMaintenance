import sqlite3


class SettingsDB:
    """
    Simple key/value settings store in SQLite.
    Replaces settings.json.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_table()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_table(self):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)
        conn.commit()
        conn.close()

    # ------------------------------------------------------------
    # Load all settings into a dict
    # ------------------------------------------------------------
    def load_all(self) -> dict:
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT key, value FROM settings")
        rows = cur.fetchall()
        conn.close()

        settings = {}
        for k, v in rows:
            settings[k] = v
        return settings

    # ------------------------------------------------------------
    # Get a single setting
    # ------------------------------------------------------------
    def get(self, key: str, default=None):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cur.fetchone()
        conn.close()
        if row is None:
            return default
        return row[0]

    # ------------------------------------------------------------
    # Set a setting
    # ------------------------------------------------------------
    def set(self, key: str, value):
        conn = self._connect()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, str(value)))
        conn.commit()
        conn.close()
