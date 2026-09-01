# Bayesian Blueprints: Electric Vehicle Range Prediction

A machine learning solution and interactive web application for predicting Electric Vehicle (EV) driving range (`range_km`) from physical and technical specifications without data leakage.

## Project Structure

```text
Bayesian Blueprints/
├── data/
│   ├── 48c74e3c-91ff-4dda-ba7e-0939da12cf70.xls   # Raw Excel dataset
│   └── raw.csv                                    # Converted CSV dataset
├── ev-range-web/                                  # Web Application (Flask + Vanilla JS/CSS)
│   ├── app.py                                     # Flask application server
│   ├── requirements.txt                           # Web app dependencies
│   ├── scripts/
│   │   └── test_predictions.py                    # Prediction variability audit script
│   ├── templates/                                 # Multi-page Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── predictor.html
│   │   ├── model.html
│   │   └── insights.html
│   └── static/                                    # Static assets (CSS, JS, plots)
├── model/
│   └── ev_range_pipeline.joblib                   # Serialized scikit-learn pipeline
├── notebook/
│   └── main.ipynb                                 # End-to-end analysis & modeling notebook
├── plots/
│   ├── Model comparison.png                       # Cross-validation performance plot
│   ├── Predicted vs actual range.png               # Actual vs predicted scatter plot
│   └── Feature importances.png                    # Feature importance bar chart
├── MODEL_EXPLANATION.md                           # Detailed model breakdown & technical report
├── README.md                                      # Project overview & quickstart
└── problem.pdf                                    # Project specification problem statement
```

## Quick Summary

- **Objective**: Predict EV range (`range_km`) based on battery capacity, vehicle dimensions, weight, seating, and performance specs.
- **Target Leakage Control**: `efficiency_wh_per_km` was strictly excluded from modeling inputs as instructed.
- **Best Model**: **Gradient Boosting Regressor** (tuned via GridSearchCV).
- **Test Performance** ($N=96$ held-out EV models):
  - **$R^2$ Score**: `0.9813`
  - **MAE**: `10.82 km`
  - **RMSE**: `14.08 km`
- **Key Predictive Features**:
  1. `battery_per_seat` (49.99%)
  2. `battery_capacity_kWh` (34.03%)
  3. `height_mm` (5.12%)
  4. `fast_charging_power_kw_dc` (3.48%)

For the complete technical breakdown, feature engineering math, data audit findings, and hyperparameter tuning details, see [MODEL_EXPLANATION.md](file:///p:/NIT/Projects/Bayesian%20Blueprints/MODEL_EXPLANATION.md).

## Running the Web Application

```bash
cd ev-range-web
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

## Model Inference API Example

```python
import joblib
import pandas as pd

# Load the trained pipeline
pipeline = joblib.load("model/ev_range_pipeline.joblib")

# Sample vehicle specs
sample_data = pd.DataFrame([{
    'top_speed_kmh': 180,
    'battery_capacity_kWh': 77.4,
    'number_of_cells': 384,
    'torque_nm': 350,
    'acceleration_0_100_s': 7.3,
    'fast_charging_power_kw_dc': 233,
    'towing_capacity_kg': 1600,
    'seats': 5,
    'length_mm': 4635,
    'width_mm': 1890,
    'height_mm': 1605,
    'cargo_volume_l': '520',
    'drivetrain': 'RWD',
    'segment': 'JC - Medium',
    'car_body_type': 'SUV',
    'cells_missing_flag': 0,
    'footprint_m2': 8.76,
    'volume_m3': 14.06,
    'battery_per_seat': 15.48,
    'torque_per_100kwh': 452.19,
    'segment_group': 'JC'
}])

# Predict range in km
range_pred = pipeline.predict(sample_data)[0]
print(f"Predicted EV Range: {range_pred:.2f} km")
```
