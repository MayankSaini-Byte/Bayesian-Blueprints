# EV Range Predictor — Model Architecture & Explanation

This document serves as a presentation-ready overview of the Machine Learning pipeline built by **Team Bayesian Blueprints**.

## 1. Problem Statement
The objective is to predict an electric vehicle's official driving range (`range_km`) entirely from its static engineering specifications (battery capacity, dimensions, drivetrain, weight, charging speed, etc.) without relying on trip-level telemetry or algebraic shortcuts.

**Target Variable**: `range_km` (official driving range)
**Crucial Constraint**: `efficiency_wh_per_km` was strictly excluded from training because range, battery capacity, and efficiency are algebraically linked. Including it would allow the model to simply calculate the answer rather than genuinely learn from the engineering specs.

## 2. Dataset & Preprocessing
The model was trained on a dataset of **478 EV models**, split into 391 training rows and 87 test rows. 
A grouped shuffle split (grouped by brand and model family) was used to ensure that closely related vehicle trims cannot appear in both the training and test sets, simulating true real-world generalisation.

### Pipeline Architecture
The input data flows through a strict Scikit-Learn `ColumnTransformer` to prevent data leakage:
- **Numeric Features (19 inputs)**: Processed via `SimpleImputer(strategy='median')` and `StandardScaler()`. Missing values in specific numeric columns (like cell count or cargo volume) trigger explicit missingness flags, so the model learns from the absence of data rather than blindly trusting the median.
- **Categorical Features (3 inputs)**: `drivetrain`, `segment`, and `car_body_type` are processed via `SimpleImputer(strategy='constant', fill_value='Unknown')` and `OneHotEncoder(handle_unknown='ignore')`.

### Advanced Feature Engineering
Beyond raw specs, four domain-specific features were engineered to help the model reason about the vehicle's physics and purpose:
1. **`footprint_m2`**: Length × Width (proxy for drag area)
2. **`volume_m3`**: Footprint × Height (bounding box volume)
3. **`battery_per_seat`**: Battery Capacity / Seats (generosity of battery relative to passenger load)
4. **`torque_per_100kwh`**: Torque / Battery Capacity (distinguishes performance-tuned drivetrains from range-tuned drivetrains)

## 3. Model Selection
Seven models were evaluated using 5-fold Grouped Cross-Validation on the training set:
1. **Ridge Regression (CV RMSE: 23.74 km) 🏆 Winner**
2. Linear Regression (CV RMSE: 24.92 km)
3. Lasso Regression (CV RMSE: 25.31 km)
4. Gradient Boosting (CV RMSE: 31.51 km)
5. Random Forest (CV RMSE: 34.95 km)
6. XGBoost (CV RMSE: 36.47 km)
7. Mean Baseline (CV RMSE: 104.58 km)

**Why Ridge?** 
On a dataset of 478 rows, heavy ensembles like XGBoost and Random Forest easily overfit. A regularized linear model (Ridge, $\alpha = 1$) generalised far better to unseen EV families, maintaining low variance and strong interpretability.

## 4. Final Performance (Held-Out Test Set)
Evaluated on 87 completely unseen vehicles:
- **R² Score**: 93.75%
- **MAE**: 19.19 km (Average error is just ~19 km off the official range)
- **RMSE**: 23.61 km

## 5. Feature Interpretability
Using Permutation Importance (measuring the spike in error when a feature is scrambled), the top driving factors behind the model's predictions are:
1. **Battery Capacity** (+111.76 km Δ RMSE)
2. **Height** (+43.34 km Δ RMSE)
3. **Car Body Type** (+8.97 km Δ RMSE)
4. **Top Speed** (+8.68 km Δ RMSE)
5. **Segment** (+8.64 km Δ RMSE)

Unsurprisingly, raw battery capacity is the dominating factor, but aerodynamic properties (height, body type, segment) form the critical secondary tier that refines the prediction.

## 6. Reproducibility
The complete, tuned pipeline (imputers, scalers, encoders, and the Ridge model) was serialized to `ev_range_pipeline.joblib` with a fixed random seed of `42`. This identical artifact powers the Flask web application's `/api/predict` endpoint, ensuring that production predictions perfectly match the research environment.
