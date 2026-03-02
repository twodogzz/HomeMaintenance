# HomeMaintenance

A comprehensive desktop application for managing home maintenance tasks, combining pool water chemistry tracking and rainfall monitoring into a single, user-friendly interface.

## Overview

Home Maintenance Manager is a Python-based Windows application that consolidates two previously separate tools into one centralized system:
- **Pool Maintenance Tracker**: Monitor and manage swimming pool water chemistry tests
- **Rainfall Logger**: Track rainfall data for lawn watering decisions

## Features

### Pool Tests
- Record pool water chemistry measurements (pH, chlorine, alkalinity, etc.)
- Color-coded status indicators for test results (in range, high, low)
- Compare results against configurable desired ranges
- Historical test data tracking and analysis
- Calculate next recommended test dates

### Rainfall Logger
- Log daily rainfall measurements
- Track cumulative rainfall over time
- Moisture model for lawn watering decisions
- Historical rainfall data visualization
- Dashboard view with statistics

### Additional Features
- Inventory management (planned)
- Configurable settings and preferences
- SQLite database for reliable data storage
- Intuitive tabbed interface

## Technology Stack

- **Python 3.14+**
- **Tkinter** for GUI
- **SQLite** for data persistence
- **tkcalendar** for date selection

## Database

The application uses a single SQLite database (`home_maintenance.db`) to store all data including pool test results, rainfall measurements, and application settings.
