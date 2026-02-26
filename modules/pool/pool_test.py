from dataclasses import dataclass, field
from datetime import date
from typing import Optional, Dict

from .next_test_date import next_planned_test_date
from modules.pool.classification_module import classify_value


@dataclass
class PoolTest:
    # --- Raw input fields ---
    test_date: date
    free_chlorine: float
    combined_chlorine: float
    total_chlorine: float
    salt_level: float
    alkalinity: float
    ph: float
    sunscreen: float
    hardness: float
    phosphates: float
    copper: float
    clarity_notes: str = ""
    actions_taken: str = ""

    # --- Database ID (must come AFTER non-default fields) ---

    id: Optional[int] = None
    
    # --- Derived fields ---
    next_test_date: date = field(init=False)
    classifications: Dict[str, str] = field(init=False)

    def __post_init__(self):
        # Compute next planned test date
        self.next_test_date = next_planned_test_date(self.test_date)

        # Classification results (filled later via apply_ranges())
        self.classifications = {}

    # ------------------------------------------------------------
    # Apply desired ranges to classify each numeric field
    # ------------------------------------------------------------
    def apply_ranges(self, ranges: Dict[str, Dict[str, float]]):
        """
        ranges = {
            "Alkalinity (ppm)": {"low": 80, "high": 120, "factor_warn": 0.10},
            "pH":               {"low": 7.2, "high": 7.8, "factor_warn": 0.10},
            ...
        }
        """

        numeric_fields = {
            "Free Chlorine (ppm)": self.free_chlorine,
            "Combined Chlorine (ppm)": self.combined_chlorine,
            "Total Chlorine (ppm)": self.total_chlorine,
            "Salt Level (ppm)": self.salt_level,
            "Alkalinity (ppm)": self.alkalinity,
            "pH": self.ph,
            "Sunscreen (Stabiliser) (ppm)": self.sunscreen,
            "Total Hardness (ppm)": self.hardness,
            "Phosphates (ppm)": self.phosphates,
            "Copper Total (ppm)": self.copper,
        }

        for name, value in numeric_fields.items():
            if name in ranges:
                low = ranges[name]["low"]
                high = ranges[name]["high"]
                fw = ranges[name]["factor_warn"]

                status = classify_value(value, low, high, fw)
                self.classifications[name] = status
            else:
                self.classifications[name] = "unknown"

    # ------------------------------------------------------------
    # Export to dict for SQLite or JSON
    # ------------------------------------------------------------
    def to_dict(self):
        return {
            "test_date": self.test_date.isoformat(),
            "free_chlorine": self.free_chlorine,
            "combined_chlorine": self.combined_chlorine,
            "total_chlorine": self.total_chlorine,
            "salt_level": self.salt_level,
            "alkalinity": self.alkalinity,
            "ph": self.ph,
            "sunscreen": self.sunscreen,
            "hardness": self.hardness,
            "phosphates": self.phosphates,
            "copper": self.copper,
            "clarity_notes": self.clarity_notes,
            "actions_taken": self.actions_taken,
            "next_test_date": self.next_test_date.isoformat(),
            "classifications": self.classifications,
        }

    # ------------------------------------------------------------
    # Factory method for UI or database loading
    # ------------------------------------------------------------
    @staticmethod
    def from_dict(d: Dict):
        obj = PoolTest(
            test_date=date.fromisoformat(d["test_date"]),
            free_chlorine=d["free_chlorine"],
            combined_chlorine=d["combined_chlorine"],
            total_chlorine=d["total_chlorine"],
            salt_level=d["salt_level"],
            alkalinity=d["alkalinity"],
            ph=d["ph"],
            sunscreen=d["sunscreen"],
            hardness=d["hardness"],
            phosphates=d["phosphates"],
            copper=d["copper"],
            clarity_notes=d.get("clarity_notes", ""),
            actions_taken=d.get("actions_taken", "")
        )

        # Apply ranges if provided
        if "ranges" in d:
            obj.apply_ranges(d["ranges"])

        return obj
