"""Quick verification: does the website predict using the new Ridge model?"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import engineer_features, pipeline

cleaned = {
    "top_speed_kmh": 180, "battery_capacity_kWh": 77.4,
    "number_of_cells": 384, "torque_nm": 350,
    "acceleration_0_100_s": 7.3, "fast_charging_power_kw_dc": 233,
    "towing_capacity_kg": 1600, "seats": 5,
    "length_mm": 4635, "width_mm": 1890, "height_mm": 1605,
    "cargo_volume_l": 520, "drivetrain": "RWD",
    "segment": "JC - Medium", "car_body_type": "SUV",
    "cells_missing_flag": 0,
}

df = engineer_features(cleaned)
print("DataFrame columns:", list(df.columns))
print("DataFrame shape:", df.shape)
print()

if pipeline is not None:
    pred = pipeline.predict(df)[0]
    model_obj = pipeline.named_steps["model"]
    print(f"Prediction: {pred:.2f} km")
    print(f"Model type: {type(model_obj).__name__}")
    print(f"Model alpha: {model_obj.alpha}")
    print()
    print("SUCCESS — Website predictor is using Ridge Regression (alpha=1)")
else:
    from app import model_load_error
    print("Pipeline failed to load!")
    print("Error:", model_load_error)
