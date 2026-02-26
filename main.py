import tkinter as tk
from tkinter import ttk

from modules.rainfall.rainfall_tab import RainFallTab
from modules.pool.pool_tab import PoolTestsTab
from modules.pool.pool_test_db import PoolTestDB
from modules.pool.desired_ranges import DesiredRanges


class HomeMaintenanceApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ------------------------------------------------------------
        # Window setup
        # ------------------------------------------------------------
        self.title("Home Maintenance Manager")
        self.geometry("1200x800")

        # Set main app icon
        try:
            self.iconbitmap("maintenance.ico")
        except Exception:
            pass

        # ------------------------------------------------------------
        # Shared database path
        # ------------------------------------------------------------
        self.db_path = "home_maintenance.db"

        # ------------------------------------------------------------
        # Shared resources
        # ------------------------------------------------------------
        self.ranges = DesiredRanges(self.db_path).load()
        self.pool_db = PoolTestDB(self.db_path)

        # ------------------------------------------------------------
        # Notebook (tabs)
        # ------------------------------------------------------------
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True)

        # Build tabs
        self._build_rainfall_tab()
        self._build_pool_tests_tab()
        self._build_inventory_tab()
        self._build_settings_tab()

    # ------------------------------------------------------------
    # Rainfall Tab
    # ------------------------------------------------------------
    def _build_rainfall_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Rainfall")

        rain_tab = RainFallTab(frame)
        rain_tab.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Pool Tests Tab
    # ------------------------------------------------------------
    def _build_pool_tests_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Pool Tests")

        pool_tab = PoolTestsTab(frame, self.pool_db, self.ranges)
        pool_tab.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    # Inventory Placeholder
    # ------------------------------------------------------------
    def _build_inventory_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Inventory")

        ttk.Label(frame, text="Inventory module coming soon…").pack(pady=20)

    # ------------------------------------------------------------
    # Settings Placeholder
    # ------------------------------------------------------------
    def _build_settings_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Settings")

        ttk.Label(frame, text="Settings module coming soon…").pack(pady=20)


if __name__ == "__main__":
    app = HomeMaintenanceApp()
    app.mainloop()
