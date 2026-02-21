from desired_ranges import DesiredRanges
from pool_test import PoolTest
from datetime import date

# Load ranges
ranges = DesiredRanges("home_maintenance.db").load()
print("Loaded ranges:", ranges)

# Create a sample test
test = PoolTest(
    test_date=date(2025, 2, 10),
    free_chlorine=11.73,
    combined_chlorine=1.07,
    total_chlorine=12.81,
    salt_level=4609,
    alkalinity=123,
    ph=7.8,
    sunscreen=29,
    hardness=237,
    phosphates=0.172,
    copper=0.1,
    clarity_notes="Clear",
    actions_taken="Set chlorinator 70%"
)

# Apply ranges
test.apply_ranges(ranges)

print("\nClassification results:")
for k, v in test.classifications.items():
    print(f"{k:35} → {v}")
