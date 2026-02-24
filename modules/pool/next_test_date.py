# ---------------------------------------------------------------------
# Next Planned Test Date Module
# ---------------------------------------------------------------------
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def next_planned_test_date(d):
    """
    Reproduces the Excel VBA logic exactly:

    1. Add one month to the test date.
    2. Move forward to the first Tuesday on or after that date.
    """
    base = d + relativedelta(months=+1)
    next_date = base

    # Python weekday(): Monday=0, Tuesday=1
    while next_date.weekday() != 1:
        next_date += timedelta(days=1)

    return next_date


# ---------------------------------------------------------------------
# Validation dataset (Excel → expected results)
# ---------------------------------------------------------------------
tests = [
    ("18/12/2024", "Tue 21 Jan '25"),
    ("6/01/2025",  "Tue 11 Feb '25"),
    ("10/01/2025", "Tue 11 Feb '25"),
    ("3/02/2025",  "Tue 04 Mar '25"),
    ("10/02/2025", "Tue 11 Mar '25"),
    ("17/02/2025", "Tue 18 Mar '25"),
    ("25/02/2025", "Tue 25 Mar '25"),
    ("2/04/2025",  "Tue 06 May '25"),
    ("28/04/2025", "Tue 03 Jun '25"),
    ("26/06/2025", "Tue 29 Jul '25"),
    ("31/07/2025", "Tue 02 Sep '25"),
    ("8/09/2025",  "Tue 14 Oct '25"),
    ("8/10/2025",  "Tue 11 Nov '25"),
    ("18/11/2025", "Tue 23 Dec '25"),
    ("5/12/2025",  "Tue 06 Jan '26"),
    ("3/01/2026",  "Tue 03 Feb '26"),
    ("28/01/2026", "Tue 03 Mar '26"),
]


# ---------------------------------------------------------------------
# Run validation
# ---------------------------------------------------------------------
if __name__ == "__main__":
    print("Validating next_planned_test_date() against Excel results:\n")

    for test_date_str, excel_result in tests:
        d = datetime.strptime(test_date_str, "%d/%m/%Y").date()
        py_date = next_planned_test_date(d)
        py_str = py_date.strftime("%a %d %b '%y")
        match = "MATCH" if py_str == excel_result else "MISMATCH"

        print(f"{test_date_str:12} → {py_str:15} → {match}")

    print("\nValidation complete.")
