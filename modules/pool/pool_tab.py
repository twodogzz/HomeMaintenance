import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date
from modules.pool.pool_test import PoolTest

# High‑contrast text colours (Palette A)
STATUS_COLOURS = {
    "in_range":        "#006400",   # dark green
    "slightly_high":   "#B8860B",   # dark goldenrod
    "high":            "#8B0000",   # dark red
    "slightly_low":    "#1E90FF",   # dodger blue
    "low":             "#00008B",   # dark blue
    "unknown":         "#000000",   # black
}


class PoolTestsTab(ttk.Frame):
    def __init__(self, parent, db, ranges):
        super().__init__(parent)

        self.db = db
        self.ranges = ranges
        self.selected_id = None

        # Transparent 1×1 image required for per‑cell styling
        self._img = tk.PhotoImage(width=1, height=1)

        self._build_ui()
        self._refresh_table()

    # ------------------------------------------------------------
    # UI Layout
    # ------------------------------------------------------------
    def _build_ui(self):
        form = ttk.LabelFrame(self, text="Enter / Edit Pool Test")
        form.pack(fill="x", padx=10, pady=5)

        # Row 0
        ttk.Label(form, text="Date:").grid(row=0, column=0, sticky="e")
        self.entry_date = DateEntry(form, width=12, date_pattern="yyyy-mm-dd")
        self.entry_date.grid(row=0, column=1, padx=5)

        ttk.Label(form, text="Free Chlorine:").grid(row=0, column=2, sticky="e")
        self.entry_fc = ttk.Entry(form, width=8)
        self.entry_fc.grid(row=0, column=3, padx=5)

        ttk.Label(form, text="Combined Chlorine:").grid(row=0, column=4, sticky="e")
        self.entry_cc = ttk.Entry(form, width=8)
        self.entry_cc.grid(row=0, column=5, padx=5)

        # Row 1
        ttk.Label(form, text="Total Chlorine:").grid(row=1, column=0, sticky="e")
        self.entry_tc = ttk.Entry(form, width=8)
        self.entry_tc.grid(row=1, column=1, padx=5)

        ttk.Label(form, text="Salt Level:").grid(row=1, column=2, sticky="e")
        self.entry_salt = ttk.Entry(form, width=8)
        self.entry_salt.grid(row=1, column=3, padx=5)

        ttk.Label(form, text="Alkalinity:").grid(row=1, column=4, sticky="e")
        self.entry_alk = ttk.Entry(form, width=8)
        self.entry_alk.grid(row=1, column=5, padx=5)

        # Row 2
        ttk.Label(form, text="pH:").grid(row=2, column=0, sticky="e")
        self.entry_ph = ttk.Entry(form, width=8)
        self.entry_ph.grid(row=2, column=1, padx=5)

        ttk.Label(form, text="Sunscreen:").grid(row=2, column=2, sticky="e")
        self.entry_sunscreen = ttk.Entry(form, width=8)
        self.entry_sunscreen.grid(row=2, column=3, padx=5)

        ttk.Label(form, text="Hardness:").grid(row=2, column=4, sticky="e")
        self.entry_hard = ttk.Entry(form, width=8)
        self.entry_hard.grid(row=2, column=5, padx=5)

        # Row 3
        ttk.Label(form, text="Phosphates:").grid(row=3, column=0, sticky="e")
        self.entry_phos = ttk.Entry(form, width=8)
        self.entry_phos.grid(row=3, column=1, padx=5)

        ttk.Label(form, text="Copper:").grid(row=3, column=2, sticky="e")
        self.entry_copper = ttk.Entry(form, width=8)
        self.entry_copper.grid(row=3, column=3, padx=5)

        # Row 4 — Notes
        ttk.Label(form, text="Clarity Notes:").grid(row=4, column=0, sticky="ne")
        self.entry_notes = tk.Text(form, width=40, height=3)
        self.entry_notes.grid(row=4, column=1, columnspan=5, sticky="w", pady=3)

        ttk.Label(form, text="Actions Taken:").grid(row=5, column=0, sticky="ne")
        self.entry_actions = tk.Text(form, width=40, height=3)
        self.entry_actions.grid(row=5, column=1, columnspan=5, sticky="w", pady=3)

        # Buttons
        btn_frame = ttk.Frame(form)
        btn_frame.grid(row=6, column=0, columnspan=6, pady=5)

        ttk.Button(btn_frame, text="Add Test", command=self._on_add).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Update Selected", command=self._on_update).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Delete Selected", command=self._on_delete).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self._refresh_table).pack(side="left", padx=5)

        # ---------- Table ----------
        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.cols = (
            "ID", "Date", "FC", "CC", "TC", "Salt", "Alk", "pH",
            "Sun", "Hard", "Phos", "Cu", "Next Test", "Notes"
        )

        self.tree = ttk.Treeview(table_frame, columns=self.cols, show="headings")
        for c in self.cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=90 if c != "Notes" else 200)

        self.tree.pack(side="left", fill="both", expand=True)

        scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    # ------------------------------------------------------------
    # Table Refresh
    # ------------------------------------------------------------
    def _refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        tests = self.db.list_all()

        col_to_key = {
            "FC":   "Free Chlorine (ppm)",
            "CC":   "Combined Chlorine (ppm)",
            "TC":   "Total Chlorine (ppm)",
            "Salt": "Salt Level (ppm)",
            "Alk":  "Alkalinity (ppm)",
            "pH":   "pH",
            "Sun":  "Sunscreen (Stabiliser) (ppm)",
            "Hard": "Total Hardness (ppm)",
            "Phos": "Phosphates (ppm)",
            "Cu":   "Copper Total (ppm)",
        }

        style = ttk.Style()

        for t in tests:
            t.apply_ranges(self.ranges)

            row = (
                t.id,
                t.test_date.isoformat(),
                t.free_chlorine,
                t.combined_chlorine,
                t.total_chlorine,
                t.salt_level,
                t.alkalinity,
                t.ph,
                t.sunscreen,
                t.hardness,
                t.phosphates,
                t.copper,
                t.next_test_date.isoformat(),
                t.clarity_notes,
                t.actions_taken,   # not shown in table, but needed for selection
            )

            item_id = self.tree.insert("", "end", values=row)

            # Apply per‑cell styles
            for col, key in col_to_key.items():
                status = t.classifications.get(key, "unknown")
                colour = STATUS_COLOURS.get(status, "#000000")

                style_name = f"Cell_{item_id}_{col}.Treeview"
                style.configure(style_name, foreground=colour, font=("Segoe UI", 9, "bold"))

                # Force per‑cell rendering using image trick
                self.tree.set(item_id, col, self.tree.set(item_id, col))
                self.tree.item(item_id, image=self._img, tags=(style_name,))

    # ------------------------------------------------------------
    # Row Selection
    # ------------------------------------------------------------
    def _on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return

        item = self.tree.item(sel[0])
        vals = item["values"]

        self.selected_id = int(vals[0])

        self.entry_date.set_date(vals[1])
        self.entry_fc.delete(0, "end"); self.entry_fc.insert(0, vals[2])
        self.entry_cc.delete(0, "end"); self.entry_cc.insert(0, vals[3])
        self.entry_tc.delete(0, "end"); self.entry_tc.insert(0, vals[4])
        self.entry_salt.delete(0, "end"); self.entry_salt.insert(0, vals[5])
        self.entry_alk.delete(0, "end"); self.entry_alk.insert(0, vals[6])
        self.entry_ph.delete(0, "end"); self.entry_ph.insert(0, vals[7])
        self.entry_sunscreen.delete(0, "end"); self.entry_sunscreen.insert(0, vals[8])
        self.entry_hard.delete(0, "end"); self.entry_hard.insert(0, vals[9])
        self.entry_phos.delete(0, "end"); self.entry_phos.insert(0, vals[10])
        self.entry_copper.delete(0, "end"); self.entry_copper.insert(0, vals[11])

        self.entry_notes.delete("1.0", "end")
        self.entry_notes.insert("1.0", vals[13])

        self.entry_actions.delete("1.0", "end")
        self.entry_actions.insert("1.0", vals[14])

    # ------------------------------------------------------------
    # Add / Update / Delete
    # ------------------------------------------------------------
    def _on_add(self):
        data = self._collect_form()
        test = PoolTest(**data)
        test.apply_ranges(self.ranges)
        self.db.insert(test)
        self._refresh_table()

    def _on_update(self):
        if not self.selected_id:
            return
        data = self._collect_form()
        test = PoolTest(**data)
        test.apply_ranges(self.ranges)
        self.db.update(self.selected_id, test)
        self._refresh_table()

    def _on_delete(self):
        if not self.selected_id:
            return
        self.db.delete(self.selected_id)
        self._refresh_table()

    # ------------------------------------------------------------
    # Helper: Collect form data
    # ------------------------------------------------------------
    def _collect_form(self):
        return {
            "test_date": date.fromisoformat(self.entry_date.get()),
            "free_chlorine": float(self.entry_fc.get()),
            "combined_chlorine": float(self.entry_cc.get()),
            "total_chlorine": float(self.entry_tc.get()),
            "salt_level": float(self.entry_salt.get()),
            "alkalinity": float(self.entry_alk.get()),
            "ph": float(self.entry_ph.get()),
            "sunscreen": float(self.entry_sunscreen.get()),
            "hardness": float(self.entry_hard.get()),
            "phosphates": float(self.entry_phos.get()),
            "copper": float(self.entry_copper.get()),
            "clarity_notes": self.entry_notes.get("1.0", "end").strip(),
            "actions_taken": self.entry_actions.get("1.0", "end").strip(),
        }
