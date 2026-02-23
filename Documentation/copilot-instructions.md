# Copilot Instructions for Home Maintenance App

## Project Overview
A Tkinter-based home maintenance tracking application with SQLite backend. Manages pool water chemistry testing and rainfall data with configurable parameter ranges and visual status classification.

## Architecture

### Domain Structure
- **Pool Testing Module**: `PoolTest` (dataclass), `PoolTestDB` (CRUD operations), `pool_tests_tab.py` (UI)
- **Rainfall Module**: `RainfallRecord` (data container), `RainfallDB` (CRUD operations), `rain_app.py` (UI)
- **Configuration**: `DesiredRanges` (load ranges from DB), `SettingsDB` (key/value store)
- **Main Entry**: `HomeMaintenanceApp` (Tkinter root, tabs manager)

### Key Files
- [pool_test.py](../pool_test.py) - Domain model with field validation and classification
- [pool_test_db.py](../pool_test_db.py) - Pool test persistence layer (~269 lines)
- [classification_module.py](../classification_module.py) - Status classification logic (mirrors Excel VBA)
- [pool_tests_tab.py](../pool_tests_tab.py) - UI tab with data grid and form
- [rainfall_db.py](../rainfall_db.py) - Rainfall data persistence
- [settings_db.py](../settings_db.py) - Key/value settings store

### Database
Single file: `home_maintenance.db` (SQLite3)

**Core Tables:**
- `pool_tests`: id, test_date, free_chlorine, combined_chlorine, total_chlorine, salt_level, alkalinity, ph, sunscreen, hardness, phosphates, copper, clarity_notes, actions_taken, next_test_date
- `rainfall`: id, date, rain_mm, bom_mm, notes, watered, moisture
- `settings`: key, value (key-value store)
- `desired_ranges`: item_name, low_value, high_value, factor_warn

All tables created via `CREATE TABLE IF NOT EXISTS` on application startup.

## Critical Patterns

### Data Flow
1. **Domain model** imports ranges from `DesiredRanges.load()` (caches in memory)
2. **PoolTest.apply_ranges()** classifies 10 numeric fields against loaded ranges
3. **Classification results** stored in `classifications` dict keyed by field name
4. **UI layer** colors cells based on classification status

### Classification Logic (Must-Understand)
```python
# classification_module.py: classify_value(value, low, high, factor_warn)
# Returns one of: in_range, slightly_high, high, slightly_low, low
#
# Logic mirrors Excel VBA:
# - slightly_high/low = within factor_warn margin (10% default)
# - high/low = outside acceptable range
# Ex: pH range 7.2-7.8 with factor_warn=0.10
#     acceptable range = 6.48-8.58
#     7.0 → slightly_low (between 6.48 and 7.2)
#     6.0 → low (below 6.48)
```

### PoolTest Data Model Pattern
- Dataclass with `@dataclass` decorator
- Post-init auto-calculates `next_test_date` via `next_planned_test_date()`
- Fields must be defined before defaults in dataclass
- Status `classifications` dict populated by calling `apply_ranges(ranges_dict)`

### Database Wrapper Pattern
```python
class XxxDB:
    def __init__(self, db_path: str):
        self.db_path = db_path
    def _connect(self):
        return sqlite3.connect(self.db_path)
    # CRUD methods use ? placeholders for parameterized queries
```
All wrapper classes follow this pattern. Always use parameterized queries, never f-strings for SQL.

### Tab UI Pattern
- Subclass `ttk.Frame`
- Receive `parent` (notebook), DB instance, and shared resources
- Build widgets in `_build_ui()` 
- Refresh data in `_refresh_table()`
- Entry fields use naming convention `self.entry_<fieldname>`

### Color Status Mapping
```python
# classification_module.py defines STATUS_COLOURS
# Replicated in pool_tests_tab.py for UI rendering (different hex codes for contrast)
# Values: in_range (green), slightly_high (yellow), high (orange),
#         slightly_low (lightblue), low (blue), unknown (white)
```

## Developer Workflows

### Adding a New Pool Test Field
1. Add field to `PoolTest` dataclass in [pool_test.py](../pool_test.py)
2. Add INSERT/UPDATE column to `PoolTestDB` methods in [pool_test_db.py](../pool_test_db.py)
3. Add entry widget to form in [pool_tests_tab.py](../pool_tests_tab.py)
4. Add mapping in `PoolTest.apply_ranges()` if numeric field needing classification
5. Add desired_range row to `desired_ranges` table via SQL or migration
6. Migrate existing data if needed

### Testing
- [test_update_pool_test_db.py](../test_update_pool_test_db.py) - Full insert/update/load cycle
- [test_ranges_loader.py](../test_ranges_loader.py) - Range loading validation
- Run tests directly: `python path/to/test_file.py`
- Migration scripts: [migration_rainfall.py](../migration_rainfall.py), [migration_pool_tests.py](../migration_pool_tests.py)

### Database Initialization
- Application automatically creates tables on first run
- Ranges must be populated: `INSERT INTO desired_ranges VALUES (...)`
- Use [init_db.sql](../init_db.sql) for schema + seed data
- Settings can be loaded from [settings.json](../settings.json) or initialized via UI

## Project Conventions

### Naming
- Data containers and domain models: PascalCase (`PoolTest`, `RainfallRecord`)
- Database wrappers: `XxxDB` postfix (`PoolTestDB`, `RainfallDB`)
- Tab UI classes: `XxxTab` postfix (`PoolTestsTab`)
- Private methods: `_method_name()`

### SQL Standards
- Always use parameterized queries: `(?, ?)` placeholders
- Never construct SQL with f-strings or string concatenation
- Use `ON CONFLICT(key) DO UPDATE` for upsert patterns
- Dates stored as ISO format strings: `date.isoformat()` / `"YYYY-MM-DD"`

### Type Hints
Use type hints throughout: `def method(param: Type) -> ReturnType:`
Common types: `Optional[float]`, `List[PoolTest]`, `Dict[str, str]`

### Entry Widgets
Tkinter entry fields default to empty strings. Always validate and convert:
```python
value = float(self.entry_field.get()) if self.entry_field.get() else None
```

## Integration Points

### Shared State in Main App
- `self.db_path = "home_maintenance.db"` - Single source of truth
- `self.ranges = DesiredRanges(self.db_path).load()` - Loaded once, passed to tabs
- `self.pool_db = PoolTestDB(self.db_path)` - Single instance shared across tabs

### Cross-Tab Communication
Tabs receive shared resources in constructor. If changes in one tab need to reflect in another, call refresh methods or reload ranges. No pub/sub system; use direct method calls.

### External Data
- [rain_data.csv](../rain_data.csv) - Legacy rainfall data (usually migrated to DB)
- [settings.json](../settings.json) - Legacy settings (usually migrated to DB)
- Migration occurs via `migration_*.py` scripts on app updates

## Common Tasks

### Query Latest Test
```python
db = PoolTestDB("home_maintenance.db")
latest = db.load_latest()  # Returns PoolTest or None
```

### Update Classification Status
```python
test.apply_ranges(ranges)  # Populates test.classifications dict
# Access: test.classifications["pH"] → "in_range" / "slightly_high" / etc.
```

### Add New Setting
```python
settings_db = SettingsDB("home_maintenance.db")
settings_db.set("key_name", "value")
```

## Debugging Tips
- Database path always: `home_maintenance.db` (relative to app root)
- Check `classification_module.py` test harness for classification logic verification
- Enable `print()` debugging; app has no logging framework
- Ensure dates are valid: `datetime.strptime(date_str, "%Y-%m-%d")`
- Tkinter GUI issues: test widgets in isolation first
