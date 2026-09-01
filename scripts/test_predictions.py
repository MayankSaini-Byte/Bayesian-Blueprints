"""
Test script: verify prediction variability with 3 drastically different EVs.
Run from ev-range-web/ directory.
"""
import json
import os
import sys
import re
import numpy as np
import pandas as pd
import joblib

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "ev_range_pipeline.joblib")
pipeline = joblib.load(MODEL_PATH)

SEGMENT_GROUP_RE = re.compile(r"([A-Za-z]+)\s*-")

def engineer_features(raw):
    length_m = raw["length_mm"] / 1000
    width_m = raw["width_mm"] / 1000
    height_m = raw["height_mm"] / 1000
    footprint = length_m * width_m
    volume = footprint * height_m
    seats = raw["seats"]
    battery = raw["battery_capacity_kWh"]
    torque = raw["torque_nm"]
    battery_per_seat = battery / seats if seats > 0 else 0.0
    torque_per_100kwh = (torque / battery * 100) if battery > 0 else 0.0
    seg = raw["segment"]
    match = SEGMENT_GROUP_RE.search(seg)
    segment_group = match.group(1) if match else seg

    row = {
        "top_speed_kmh": raw["top_speed_kmh"],
        "battery_capacity_kWh": battery,
        "number_of_cells": raw.get("number_of_cells", np.nan),
        "torque_nm": torque,
        "acceleration_0_100_s": raw["acceleration_0_100_s"],
        "fast_charging_power_kw_dc": raw["fast_charging_power_kw_dc"],
        "towing_capacity_kg": raw["towing_capacity_kg"],
        "seats": seats,
        "length_mm": raw["length_mm"],
        "width_mm": raw["width_mm"],
        "height_mm": raw["height_mm"],
        "cargo_volume_l": str(raw["cargo_volume_l"]),
        "drivetrain": raw["drivetrain"],
        "segment": seg,
        "car_body_type": raw["car_body_type"],
        "cells_missing_flag": raw.get("cells_missing_flag", 0),
        "footprint_m2": footprint,
        "volume_m3": volume,
        "battery_per_seat": battery_per_seat,
        "torque_per_100kwh": torque_per_100kwh,
        "segment_group": segment_group,
    }
    if raw.get("cells_missing_flag", 0) == 1:
        row["number_of_cells"] = np.nan
    return pd.DataFrame([row])


test_cases = [
    {
        "name": "A — Small compact EV (35 kWh)",
        "input": {
            "top_speed_kmh": 130, "battery_capacity_kWh": 35.0,
            "number_of_cells": None, "torque_nm": 180,
            "acceleration_0_100_s": 9.5, "fast_charging_power_kw_dc": 50,
            "towing_capacity_kg": 0, "seats": 4,
            "length_mm": 3800, "width_mm": 1680, "height_mm": 1500,
            "cargo_volume_l": 200, "drivetrain": "FWD",
            "segment": "B - Compact", "car_body_type": "Hatchback",
            "cells_missing_flag": 1,
        }
    },
    {
        "name": "B — Mid-size sedan (77 kWh)",
        "input": {
            "top_speed_kmh": 180, "battery_capacity_kWh": 77.4,
            "number_of_cells": 384, "torque_nm": 350,
            "acceleration_0_100_s": 7.3, "fast_charging_power_kw_dc": 233,
            "towing_capacity_kg": 1600, "seats": 5,
            "length_mm": 4635, "width_mm": 1890, "height_mm": 1605,
            "cargo_volume_l": 520, "drivetrain": "RWD",
            "segment": "JC - Medium", "car_body_type": "SUV",
            "cells_missing_flag": 0,
        }
    },
    {
        "name": "C — Large premium EV (110 kWh)",
        "input": {
            "top_speed_kmh": 250, "battery_capacity_kWh": 110.0,
            "number_of_cells": 600, "torque_nm": 660,
            "acceleration_0_100_s": 3.8, "fast_charging_power_kw_dc": 270,
            "towing_capacity_kg": 2500, "seats": 5,
            "length_mm": 5100, "width_mm": 2000, "height_mm": 1550,
            "cargo_volume_l": 580, "drivetrain": "AWD",
            "segment": "F - Luxury", "car_body_type": "Sedan",
            "cells_missing_flag": 0,
        }
    },
    {
        "name": "D — Battery-only change: 50 kWh (same as B otherwise)",
        "input": {
            "top_speed_kmh": 180, "battery_capacity_kWh": 50.0,
            "number_of_cells": 384, "torque_nm": 350,
            "acceleration_0_100_s": 7.3, "fast_charging_power_kw_dc": 233,
            "towing_capacity_kg": 1600, "seats": 5,
            "length_mm": 4635, "width_mm": 1890, "height_mm": 1605,
            "cargo_volume_l": 520, "drivetrain": "RWD",
            "segment": "JC - Medium", "car_body_type": "SUV",
            "cells_missing_flag": 0,
        }
    },
    {
        "name": "E — Battery-only change: 95 kWh (same as B otherwise)",
        "input": {
            "top_speed_kmh": 180, "battery_capacity_kWh": 95.0,
            "number_of_cells": 384, "torque_nm": 350,
            "acceleration_0_100_s": 7.3, "fast_charging_power_kw_dc": 233,
            "towing_capacity_kg": 1600, "seats": 5,
            "length_mm": 4635, "width_mm": 1890, "height_mm": 1605,
            "cargo_volume_l": 520, "drivetrain": "RWD",
            "segment": "JC - Medium", "car_body_type": "SUV",
            "cells_missing_flag": 0,
        }
    },
]

print("=" * 70)
print("EV RANGE PREDICTION VARIABILITY TEST")
print("=" * 70)

for tc in test_cases:
    df = engineer_features(tc["input"])
    pred = pipeline.predict(df)[0]
    bps = df["battery_per_seat"].iloc[0]
    fp = df["footprint_m2"].iloc[0]
    vol = df["volume_m3"].iloc[0]
    tpk = df["torque_per_100kwh"].iloc[0]
    sg = df["segment_group"].iloc[0]
    print(f"\n{tc['name']}")
    print(f"  battery={tc['input']['battery_capacity_kWh']} kWh  seats={tc['input']['seats']}  body={tc['input']['car_body_type']}")
    print(f"  Derived -> bps={bps:.2f}  footprint={fp:.2f}  vol={vol:.2f}  tpk={tpk:.2f}  seg_grp={sg}")
    print(f"  >>> PREDICTED RANGE: {pred:.2f} km")

print("\n" + "=" * 70)
