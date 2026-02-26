from datetime import date
from pool_test import PoolTest
from pool_test_db import PoolTestDB

db = PoolTestDB("home_maintenance.db")

# Insert a test
test = PoolTest(
    test_date=date(2025, 2, 10),
    free_chlorine=5,
    combined_chlorine=0.5,
    total_chlorine=5.5,
    salt_level=4500,
    alkalinity=110,
    ph=7.6,
    sunscreen=40,
    hardness=200,
    phosphates=0.1,
    copper=0.05,
    clarity_notes="Initial test",
    actions_taken="None"
)

test_id = db.insert(test)
print("Inserted:", test_id)

# Modify the test
test.free_chlorine = 2.5
test.ph = 7.4
test.actions_taken = "Adjusted chlorine"

db.update(test_id, test)
print("Updated.")

# Load it back
loaded = db.load(test_id)
print("Loaded free chlorine:", loaded.free_chlorine)
print("Loaded pH:", loaded.ph)
print("Loaded actions:", loaded.actions_taken)
