CREATE TABLE IF NOT EXISTS desired_ranges (
    item_name      TEXT PRIMARY KEY,
    low_value      REAL NOT NULL,
    high_value     REAL NOT NULL,
    factor_warn    REAL NOT NULL
);