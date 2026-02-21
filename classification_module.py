# ------------------------------------------------------------
# Pool Test Colour Classification Module
# ------------------------------------------------------------

def classify_value(value, low, high, factor_warn):
    """
    Classifies a numeric pool test value into one of five states:
    - in_range
    - slightly_high
    - high
    - slightly_low
    - low

    Mirrors the Excel VBA logic exactly.
    """

    acceptable_low = low - (factor_warn * low)
    acceptable_high = high + (factor_warn * high)

    if low <= value <= high:
        return "in_range"

    if high < value <= acceptable_high:
        return "slightly_high"

    if value > acceptable_high:
        return "high"

    if acceptable_low <= value < low:
        return "slightly_low"

    if value < acceptable_low:
        return "low"

    return "unknown"


# ------------------------------------------------------------
# Colour mapping for UI (hex + human-readable)
# ------------------------------------------------------------

STATUS_COLOURS = {
    "in_range":        ("#70AD47", "green"),        # Excel Accent 3
    "slightly_high":   ("#FFD966", "yellow"),       # Accent 2 (light)
    "high":            ("#FFC000", "orange"),       # Accent 2 (strong)
    "slightly_low":    ("#9DC3E6", "lightblue"),    # Accent 4 (light)
    "low":             ("#5B9BD5", "blue"),         # Accent 4 (strong)
    "unknown":         ("#FFFFFF", "white"),
}


# ------------------------------------------------------------
# Test harness
# ------------------------------------------------------------

def test_classification():
    tests = [
        # value, low, high, factor_warn, expected_status
        (7.6, 7.2, 7.8, 0.10, "in_range"),
        (8.0, 7.2, 7.8, 0.10, "slightly_high"),
        (9.0, 7.2, 7.8, 0.10, "high"),
        (7.0, 7.2, 7.8, 0.10, "slightly_low"),
        (6.0, 7.2, 7.8, 0.10, "low"),
    ]

    print("Testing classify_value():\n")

    for value, low, high, fw, expected in tests:
        result = classify_value(value, low, high, fw)
        status = "PASS" if result == expected else "FAIL"
        print(f"value={value} → {result:14} (expected {expected}) → {status}")

    print("\nTest complete.")


# ------------------------------------------------------------
# Run tests if executed directly
# ------------------------------------------------------------

if __name__ == "__main__":
    test_classification()
