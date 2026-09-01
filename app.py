"""
EV Range Prediction -- Flask Application
Serves the multi-page frontend and exposes POST /api/predict using the
serialized Gradient Boosting pipeline (model/ev_range_pipeline.joblib).
"""

import os
import re
import traceback

import joblib
import numpy as np
import pandas as pd
from flask import Flask, jsonify, render_template, request

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = Flask(__name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model", "ev_range_pipeline.joblib")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "model", "ev_range_pipeline.joblib")

pipeline = None
model_load_error = None

try:
    if os.path.exists(MODEL_PATH):
        pipeline = joblib.load(MODEL_PATH)
    else:
        model_load_error = f"File not found: {MODEL_PATH} (cwd: {os.getcwd()}, dir: {os.path.dirname(__file__)})"
except Exception as e:
    model_load_error = f"Exception loading model from {MODEL_PATH}: {type(e).__name__}: {str(e)}"
    print(model_load_error)
    traceback.print_exc()

# ---------------------------------------------------------------------------
# Feature engineering (mirrors notebook section 5)
# ---------------------------------------------------------------------------

SEGMENT_GROUP_RE = re.compile(r"([A-Za-z]+)\s*-")


def engineer_features(raw: dict) -> pd.DataFrame:
    """
    Accept validated raw user inputs and return a single-row DataFrame
    with all columns the pipeline expects (including derived features).
    """
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
        "number_of_cells": raw.get("number_of_cells"),
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

    # Handle NaN for number_of_cells when flagged as missing
    if raw.get("cells_missing_flag", 0) == 1:
        row["number_of_cells"] = np.nan

    return pd.DataFrame([row])


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

REQUIRED_NUMERIC = [
    ("top_speed_kmh", "Top speed"),
    ("battery_capacity_kWh", "Battery capacity"),
    ("torque_nm", "Torque"),
    ("acceleration_0_100_s", "Acceleration 0-100"),
    ("fast_charging_power_kw_dc", "Fast charging power"),
    ("towing_capacity_kg", "Towing capacity"),
    ("seats", "Seats"),
    ("length_mm", "Length"),
    ("width_mm", "Width"),
    ("height_mm", "Height"),
    ("cargo_volume_l", "Cargo volume"),
]

REQUIRED_CATEGORICAL = [
    ("drivetrain", "Drivetrain"),
    ("segment", "Segment"),
    ("car_body_type", "Body type"),
]


def validate(data: dict):
    """Return (cleaned_dict, errors_list)."""
    errors = []
    cleaned = {}

    if not isinstance(data, dict):
        return None, ["Request body must be a JSON object."]

    # Numeric fields
    for key, label in REQUIRED_NUMERIC:
        val = data.get(key)
        if val is None or val == "":
            errors.append(f"{label} is required.")
            continue
        try:
            val = float(val)
        except (TypeError, ValueError):
            errors.append(f"{label} must be a number.")
            continue
        cleaned[key] = val

    # Positive checks
    for key, label in [
        ("battery_capacity_kWh", "Battery capacity"),
        ("seats", "Seats"),
        ("length_mm", "Length"),
        ("width_mm", "Width"),
        ("height_mm", "Height"),
    ]:
        if key in cleaned and cleaned[key] <= 0:
            errors.append(f"{label} must be greater than 0.")

    for key, label in [
        ("fast_charging_power_kw_dc", "Fast charging power"),
        ("towing_capacity_kg", "Towing capacity"),
        ("top_speed_kmh", "Top speed"),
        ("cargo_volume_l", "Cargo volume"),
    ]:
        if key in cleaned and cleaned[key] < 0:
            errors.append(f"{label} must not be negative.")

    # Categorical fields
    for key, label in REQUIRED_CATEGORICAL:
        val = data.get(key)
        if not val or not isinstance(val, str):
            errors.append(f"{label} is required.")
        else:
            cleaned[key] = val

    # Optional: number_of_cells & cells_missing_flag
    cells_missing = int(bool(data.get("cells_missing_flag", 0)))
    cleaned["cells_missing_flag"] = cells_missing

    if cells_missing == 0:
        noc = data.get("number_of_cells")
        if noc is not None and noc != "":
            try:
                cleaned["number_of_cells"] = float(noc)
            except (TypeError, ValueError):
                errors.append("Number of cells must be a number.")
        else:
            cleaned["number_of_cells"] = np.nan
            cleaned["cells_missing_flag"] = 1
    else:
        cleaned["number_of_cells"] = np.nan

    return cleaned, errors


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/predictor")
def predictor():
    return render_template("predictor.html")


@app.route("/model")
def model_page():
    return render_template("model.html")


@app.route("/insights")
def insights():
    return render_template("insights.html")


@app.route("/api/predict", methods=["POST"])
def predict():
    if pipeline is None:
        err_detail = model_load_error or "Unknown model loading failure."
        return jsonify({"error": f"Model pipeline is not loaded. Details: {err_detail}"}), 500

    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "Invalid JSON body."}), 400

    cleaned, errors = validate(data)
    if errors:
        return jsonify({"errors": errors}), 400

    try:
        df = engineer_features(cleaned)
        prediction = pipeline.predict(df)[0]

        # Build received_input summary for the frontend
        received = {
            "battery_capacity_kWh": cleaned.get("battery_capacity_kWh"),
            "car_body_type": cleaned.get("car_body_type"),
            "drivetrain": cleaned.get("drivetrain"),
            "seats": cleaned.get("seats"),
            "top_speed_kmh": cleaned.get("top_speed_kmh"),
        }

        return jsonify({
            "predicted_range_km": round(float(prediction), 2),
            "model": "Gradient Boosting Regressor",
            "received_input": received,
        })
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Prediction failed. Check server logs."}), 500


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
