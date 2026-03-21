#!/usr/bin/env python3
"""
Background simulator for parking lot occupancy.
Run this in a separate terminal while the Flask app is running.

It connects to the same SQLite database (parking.db) and updates
occupancy values periodically with realistic random changes.
"""

import sqlite3
import time
import random
from datetime import datetime
from pathlib import Path

# ───────────────────────────────────────────────
# Configuration
# ───────────────────────────────────────────────

DB_PATH = Path("instance/parking.db")          # adjust if your db is elsewhere
# If you used "sqlite:///parking.db" → it's usually in the project root
# If you used instance folder → it's project/instance/parking.db

INTERVAL_SECONDS = 45           # how often to make changes
MIN_CHANGE = -5
MAX_CHANGE = +7
BIG_JUMP_CHANCE = 0.08          # probability of a larger jump per lot per cycle
BIG_JUMP_RANGE = (-25, +35)

# Time-of-day influence (hour → net tendency bias)
TIME_BIAS = {
    range(6, 10):   +4,     # morning arrival
    range(11, 14):  +2,     # lunch time
    range(16, 19):  -5,     # evening departure
    range(22, 24):  -3,     # late night
    range(0, 5):    -1,     # very early morning
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_current_hour_bias():
    hour = datetime.now().hour
    for hour_range, bias in TIME_BIAS.items():
        if hour in hour_range:
            return bias
    return 0

def simulate_step():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all lots
    cursor.execute("SELECT id, capacity, occupancy FROM lot")
    lots = cursor.fetchall()

    if not lots:
        print("No lots found in database.")
        conn.close()
        return

    bias = get_current_hour_bias()
    updated = 0

    for lot in lots:
        current = lot["occupancy"]
        cap = lot["capacity"]

        # Base random change
        change = random.randint(MIN_CHANGE, MAX_CHANGE)

        # Apply time-of-day bias
        low = min(-1, bias + 1)
        high = max(-1, bias + 1)
        change += random.randint(low, high)

        # Occasional big jump (event starting/ending, bus arrival, etc.)
        if random.random() < BIG_JUMP_CHANCE:
            big = random.randint(*BIG_JUMP_RANGE)
            change += big
            print(f"  Big jump on lot {lot['id']}: {big:+}")

        new_occupancy = current + change
        new_occupancy = max(0, min(cap, new_occupancy))

        if new_occupancy != current:
            cursor.execute(
                "UPDATE lot SET occupancy = ? WHERE id = ?",
                (new_occupancy, lot["id"])
            )
            updated += 1

    conn.commit()
    conn.close()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] Updated {updated}/{len(lots)} lots")

def main():
    print("Parking occupancy simulator started.")
    print(f"Database: {DB_PATH.resolve()}")
    print(f"Updates every ~{INTERVAL_SECONDS} seconds. Ctrl+C to stop.\n")

    try:
        while True:
            simulate_step()
            # Add small jitter to interval so it doesn't look too robotic
            sleep_time = INTERVAL_SECONDS + random.uniform(-12, +12)
            time.sleep(max(10, sleep_time))
    except KeyboardInterrupt:
        print("\nSimulator stopped.")

if __name__ == "__main__":
    if not DB_PATH.is_file():
        print(f"Database not found: {DB_PATH}")
        print("Make sure your Flask app has already created the database.")
        exit(1)

    main()