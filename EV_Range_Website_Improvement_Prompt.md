# EV Range Prediction Web App — UI/UX Redesign + Prediction Bug-Fix Prompt

## IMPORTANT: THIS IS A REDESIGN OF AN EXISTING PROJECT

Do not start by blindly rewriting the frontend.

First inspect the existing project, existing Flask/Python code, model-loading code, JavaScript, CSS, assets, and the `plots/` folder.

The current UI has already been built, but it is not visually strong enough. The current page is too sparse, too much like a long technical document, and not enough like a deliberately designed engineering product.

The second problem is more serious:

> **The prediction is often almost the same even when different vehicle inputs are entered.**

Treat that as a probable implementation bug until proven otherwise.

The redesign is not considered complete unless:
1. the prediction pipeline is verified with multiple deliberately different inputs,
2. the reason for repetitive predictions is identified and fixed if there is a bug,
3. the important project plots in `plots/` are actually integrated,
4. the content is split into multiple pages,
5. the visual design is substantially stronger than the current version.

---

# 01 — FIRST: AUDIT THE EXISTING PROJECT

Before changing UI code, inspect:

```text
/
├── app.py / server file
├── model/
├── plots/
├── templates/
├── static/
├── frontend files
├── Python model / preprocessing scripts
├── requirements.txt
└── README / documentation
```

Also inspect every relevant file that handles:

- form submission
- JavaScript request payload
- Flask `/api/predict`
- model loading
- feature engineering
- column names
- categorical encoding
- numerical conversion
- prediction response

Do not assume the existing implementation matches the documented model.

---

# 02 — CRITICAL BUG: PREDICTION IS TOO OFTEN THE SAME

This is the highest-priority functional issue.

The user reports that changing inputs frequently results in almost the same prediction.

Do **not** "fix" this by adding random noise.

Do **not** round aggressively.

Do **not** make the displayed number look more variable while the underlying prediction remains unchanged.

Do not hard-code a new formula to imitate model behavior.

Find the actual cause.

---

# 03 — PREDICTION DEBUGGING CHECKLIST

Run a controlled test before redesigning the prediction result UI.

Create at least these three drastically different test inputs:

### Test A — Small / low-range EV

Use a plausible compact EV:

```text
battery_capacity_kWh = 30–40
top_speed_kmh = 120–140
torque_nm = 150–220
seats = 4
length_mm = ~3500–4100
width_mm = ~1600–1800
height_mm = ~1450–1600
```

### Test B — Typical mid-size EV

Use a plausible vehicle:

```text
battery_capacity_kWh = 60–80
top_speed_kmh = 160–190
torque_nm = 250–400
seats = 5
length_mm = ~4400–4800
width_mm = ~1800–1950
height_mm = ~1500–1700
```

### Test C — Large high-capacity EV

Use a plausible larger EV:

```text
battery_capacity_kWh = 90–120+
top_speed_kmh = 200+
torque_nm = 450+
seats = 5–7
length_mm = 4800+
width_mm = 1900+
height_mm = 1600+
```

The exact test values are not important.

The important thing is that materially different inputs should result in materially different model outputs if the model is actually receiving those inputs.

Record:

```text
input JSON
→ backend received JSON
→ engineered feature dictionary
→ final DataFrame columns
→ model output
```

---

# 04 — CHECK FOR THESE COMMON CAUSES

Investigate all of the following.

## A. Frontend sends the wrong values

Check whether JavaScript is accidentally reading:

- the wrong input IDs
- the first input repeatedly
- stale form state
- hard-coded default values
- strings that are never updated
- undefined fields that are replaced with defaults

Log the final request payload in development.

Example:

```javascript
console.table(payload);
```

Do not leave excessive debug logs in the final production build, but use them while diagnosing.

---

## B. Backend ignores some submitted fields

Compare:

```text
frontend payload keys
```

against:

```text
backend expected keys
```

and against:

```text
pipeline feature columns
```

Every prediction field must have a clear path through the backend.

---

## C. Feature engineering is broken

Verify that these features are recomputed for every request:

```text
footprint_m2
volume_m3
battery_per_seat
torque_per_100kwh
segment_group
```

Do not calculate them once globally and reuse the same values for every user.

For every request:

```python
footprint_m2 = ...
volume_m3 = ...
battery_per_seat = ...
torque_per_100kwh = ...
segment_group = ...
```

---

## D. Wrong feature names

The backend DataFrame must use the exact column names expected by the trained pipeline.

Check for:

- capitalization differences
- underscore differences
- renamed fields
- `kmh` vs `km_h`
- `kWh` vs `kwh`
- `car_body_type` vs `body_type`
- missing categorical columns

Do not silently rename features without documenting why.

---

## E. Model is loading correctly but receives nearly identical data

Print or inspect the actual DataFrame sent to:

```python
pipeline.predict(...)
```

for several different requests.

Compare:

```python
df.iloc[0].to_dict()
```

across requests.

This is one of the most important debugging steps.

---

## F. Derived features are not changing

Explicitly test:

```text
battery_per_seat
footprint_m2
volume_m3
torque_per_100kwh
segment_group
```

for Test A, B and C.

If these values remain identical despite different inputs, the feature engineering path is broken.

---

## G. Incorrect preprocessing recreation

The project documentation says the complete end-to-end pipeline was serialized to:

```text
model/ev_range_pipeline.joblib
```

Use that pipeline.

Do not manually recreate:

- imputation
- scaling
- one-hot encoding

in the browser or as a separate inconsistent preprocessing path.

The model pipeline should handle the transformations it was trained to handle.

---

## H. Categorical values are invalid

Check:

```text
drivetrain
segment
car_body_type
segment_group
```

Make sure values passed from the UI match the values expected by the trained pipeline.

`handle_unknown='ignore'` may prevent crashes, but repeatedly sending unknown categories can reduce useful information.

---

## I. Missing value behavior

The model documentation specifically includes:

```text
cells_missing_flag
```

and `number_of_cells`.

Make sure:

```text
cells_missing_flag = 1
```

is used when the user marks the cell count as unavailable.

Do not accidentally send:

```text
0
```

for all vehicles.

---

## J. Numeric inputs being converted incorrectly

Check for:

```text
NaN
None
""
"undefined"
```

and accidental fallback values.

Do not silently turn invalid input into the same default number for every field.

---

# 05 — ADD A DEVELOPMENT-ONLY PREDICTION DIAGNOSTIC

Create an easy way for the developer to verify model variability.

For example, temporarily support a local diagnostic route or script:

```text
scripts/test_predictions.py
```

It should run 5–10 substantially different EV examples through the same exact production prediction function and print:

```text
Case
Battery
Weight-related proxy inputs
Dimensions
Predicted range
```

The exact feature list depends on the actual project code.

The point is to prove that input changes propagate to output changes.

Do not expose this debugging endpoint publicly in production unless explicitly needed.

---

# 06 — DO NOT CHANGE MODEL BEHAVIOR JUST TO MAKE THE UI LOOK BETTER

The visual result may be something like:

```text
421 km
```

in one case and:

```text
425 km
```

in another.

That is acceptable if the actual model produces it.

The responsibility is to make the prediction faithful to the model, not to make it appear dramatic.

If the model genuinely predicts similar values for several valid vehicles, say so.

If the model outputs are repetitive because the pipeline is broken, fix the pipeline.

---

# 07 — USE THE EXISTING `plots/` FOLDER

The project already contains important plots in:

```text
plots/
```

Inspect the folder and identify at minimum:

```text
model comparison
model vs actual
feature importance
```

Do not redraw these from memory.

Use the existing plot files where appropriate.

If the plot filenames differ, map them based on their actual content.

---

# 08 — IMPORTANT PLOT INTEGRATION RULES

The plots should not simply be dumped into a gallery.

Each plot needs context.

For each plot include:

```text
title
short interpretation
source label
```

Example:

### Model comparison

`How the candidate regressors performed during model selection.`

### Actual vs predicted

`How closely the final model tracks held-out vehicle range.`

### Feature importance

`Which engineered and raw features contribute most strongly to the Gradient Boosting model.`

Do not place three huge images one under another with no explanation.

---

# 09 — CREATE A MULTI-PAGE APPLICATION

The current long single-page structure is not desirable.

Do **not** create one giant homepage containing every section.

Use a small, coherent multi-page application.

Recommended structure:

```text
/
├── Home
├── Predictor
├── Model
└── Insights
```

Optionally:

```text
└── About / Method
```

Do not create pages merely to increase the page count.

Each page must have a clear purpose.

---

# 10 — PAGE 1: HOME

Route:

```text
/
```

Purpose:

Introduce the project and immediately direct the user to prediction.

This page should NOT contain every technical detail.

## Hero

Use a strong editorial split layout.

Example concept:

```text
EV RANGE
PREDICTION

Estimate an electric vehicle's
rated range from its engineering
specifications.

[ Try the predictor ]
```

On the opposite side:

A large restrained numeric visualization:

```text
393.18 km
DATASET MEAN

135 — 685 km
TARGET RANGE

478
VEHICLES
```

This should feel like an engineering instrument, not a marketing hero.

---

# 11 — HOME PAGE: VISUAL CHARACTER

Do not use:

- giant gradients
- glowing blobs
- floating glass panels
- neon AI patterns
- generic EV photographs
- AI-generated vehicle illustrations
- excessive rounded cards
- huge animated counters

Use:

- strong typography
- careful grid alignment
- technical annotations
- dividers
- dense/sparse rhythm
- restrained accent color
- subtle borders
- good whitespace
- editorial asymmetry

The design should feel closer to:

```text
automotive engineering interface
+
data science laboratory
+
technical publication
```

than:

```text
AI SaaS landing page
```

---

# 12 — HOME PAGE: QUICK PROJECT STATS

Use a compact row:

```text
478
EV MODELS

22
INITIAL FEATURES

80 / 20
TRAIN / TEST

42
RANDOM SEED
```

Correction:

The source documentation specifies:

```text
random seed = 42
```

Do not display `42` under a heading called `RANDOM SEED` in a way that can be confused with the train/test ratio.

Use:

```text
80 / 20
TRAIN / TEST

42
RANDOM SEED
```

---

# 13 — HOME PAGE: WHY THIS PROJECT IS INTERESTING

Use three short editorial blocks:

### Leakage Control

Efficiency is deliberately excluded because it is directly related to range.

### Domain Features

Battery-per-seat, footprint, volume and torque-related ratios add engineering context.

### Reproducibility

The preprocessing and model are packaged together into a Joblib pipeline.

These should be short, not essay-length.

---

# 14 — HOME PAGE CTA

End the primary content with one strong call to action:

```text
Have a vehicle specification sheet?

Estimate its range →

```

Click → `/predictor`

---

# 15 — PAGE 2: PREDICTOR

Route:

```text
/predictor
```

This page should be the main interactive product.

It should not feel like a giant HTML form.

---

# 16 — PREDICTOR PAGE LAYOUT

Use a desktop grid similar to:

```text
┌───────────────────────────────────────────────────────────────┐
│ PREDICTOR                                                     │
│ Enter vehicle specifications                                  │
│                                                               │
│ ┌───────────────────────────┐   ┌───────────────────────────┐ │
│ │ Performance               │   │                           │ │
│ │ Battery                   │   │      482 km               │ │
│ │ Dimensions                │   │      estimated range      │ │
│ │ Configuration             │   │                           │ │
│ │                           │   │      error context        │ │
│ │                           │   │                           │ │
│ │ [ Estimate range ]        │   │      model information    │ │
│ └───────────────────────────┘   └───────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

The right-side result panel should remain visually stable while the left-side input form changes.

---

# 17 — FORM DESIGN

Do not display 20 giant inputs in a single vertical stack.

Group inputs:

```text
01 / BATTERY
02 / PERFORMANCE
03 / DIMENSIONS
04 / CONFIGURATION
```

Use two-column subgrids where screen width allows.

Examples:

```text
Battery capacity       [ 77.4 ] kWh
Number of cells        [ 384 ]

Top speed              [ 180 ] km/h
Torque                 [ 350 ] Nm

Length                 [ 4635 ] mm
Width                  [ 1890 ] mm
Height                 [ 1605 ] mm
```

On mobile, stack naturally.

---

# 18 — PREDICTOR PAGE: INPUT UX

Inputs should have:

- clear labels
- visible units
- sensible defaults only when justified
- useful placeholders
- validation
- helpful min/max boundaries if known from actual dataset
- clear error states

Do not make users wonder what unit a number represents.

---

# 19 — PREDICTOR PAGE: DEFAULT VALUES

A default "sample vehicle" is useful.

But clearly label it:

```text
Example vehicle loaded
```

Do not make a sample prediction look like a real user prediction before interaction.

Provide:

```text
Load example
```

as a deliberate action rather than silently filling everything.

---

# 20 — PREDICTION RESULT PANEL

The result must be the strongest component on this page.

Example:

```text
ESTIMATED RANGE

482
km

Model estimate based on
vehicle specifications

────────────────────

Test MAE       10.82 km
Test RMSE      14.08 km
R²             0.9813
```

Use one large number, not multiple competing numbers.

---

# 21 — PREDICTION RESULT: ADD MODEL CONTEXT

Under the main prediction:

```text
Gradient Boosting Regressor
```

Then:

```text
Evaluation reference:
96 held-out vehicles
```

Do not imply that `10.82 km` is an uncertainty interval.

MAE is an average error metric, not a prediction confidence interval.

---

# 22 — PREDICTION RESULT: SHOW INPUT SUMMARY AFTER PREDICTION

After prediction, show a compact summary:

```text
BATTERY
77.4 kWh

BODY
SUV

DRIVETRAIN
RWD

SEATS
5
```

This gives the user confidence that the backend received the intended input.

This is also useful for debugging the "same prediction" problem.

---

# 23 — PREDICTOR PAGE: MODEL TRANSPARENCY

Add a small technical drawer or expandable panel:

```text
Why this result?

The model combines raw EV specifications with engineered features such as:

• battery per seat
• vehicle footprint
• approximate vehicle volume
• torque per 100 kWh
• segment group
```

Keep it concise.

---

# 24 — PREDICTOR PAGE: LEAKAGE NOTE

Place a small technical note near the form:

```text
EFFICIENCY IS EXCLUDED

Efficiency is not accepted as an input because it is algebraically linked
to range and could introduce target leakage.
```

This is one of the strongest technical aspects of the project.

Do not hide it.

---

# 25 — PAGE 3: MODEL

Route:

```text
/model
```

Purpose:

Explain the ML system.

This page should feel like a technical case study.

---

# 26 — MODEL PAGE: PERFORMANCE HERO

Use:

```text
MODEL PERFORMANCE

Gradient Boosting Regressor

98.13%
R²

10.82 km
MAE

14.08 km
RMSE
```

Under that:

```text
Evaluated on 96 held-out vehicles.
```

Avoid marketing language such as:

```text
industry-leading
revolutionary
state-of-the-art
```

The dataset is small, so stay credible.

---

# 27 — MODEL PAGE: USE THE EXISTING MODEL COMPARISON PLOT

Find the existing model comparison plot in:

```text
plots/
```

Show it in a large but controlled frame.

Next to or below it:

```text
MODEL SELECTION

Six regression families were benchmarked using 5-fold cross-validation.

Ridge had the strongest initial CV RMSE.
Gradient Boosting became the final held-out test winner after tuning.
```

This distinction is important.

Do not say:

```text
Gradient Boosting had the best CV score.
```

because the project documentation does not support that.

---

# 28 — MODEL PAGE: COMPARISON DATA

Use the documented CV values accurately:

| Model | 5-Fold CV Mean RMSE |
|---|---:|
| Ridge Regression | 19.57 km |
| Gradient Boosting Regressor | 22.53 km |
| Lasso Regression | 24.85 km |
| XGBoost Regressor | 24.88 km |
| Random Forest Regressor | 24.94 km |
| Linear Regression | 33.07 km |

Then explain:

```text
The final model selection should be understood from both model-selection
and held-out evaluation results rather than from one metric alone.
```

---

# 29 — MODEL PAGE: FINAL TEST COMPARISON

Show:

| Metric | Ridge | Gradient Boosting |
|---|---:|---:|
| MAE | 13.96 km | 10.82 km |
| RMSE | 17.61 km | 14.08 km |
| R² | 0.9707 | 0.98126 |

Visually emphasize Gradient Boosting.

Do not invent metrics for the other benchmark models.

---

# 30 — MODEL PAGE: PIPELINE VISUAL

Create a refined technical flow:

```text
RAW SPECIFICATIONS
        ↓
DOMAIN FEATURE ENGINEERING
        ↓
COLUMN TRANSFORMER
 ┌──────────────┬─────────────────┐
 │ Numeric      │ Categorical     │
 │ median       │ most frequent   │
 │ imputation   │ imputation      │
 │ + scaling    │ + one-hot       │
 └──────────────┴─────────────────┘
        ↓
GRADIENT BOOSTING
        ↓
PREDICTED RANGE
```

Use clean lines and typography.

Do not use glowing AI-network graphics.

---

# 31 — MODEL PAGE: FEATURE ENGINEERING

Explain the five domain features:

```text
footprint_m2
volume_m3
battery_per_seat
torque_per_100kwh
segment_group
```

Use concise formulas where useful.

Example:

```text
battery_per_seat =
battery_capacity_kWh / seats
```

Do not overwhelm the user with LaTeX.

Plain technical notation is acceptable.

---

# 32 — MODEL PAGE: REPRODUCIBILITY

Show a small technical specification panel:

```text
DATASET
478 EV models

TRAIN / TEST
382 / 96

SPLIT
80 / 20

RANDOM SEED
42

MODEL ARTIFACT
model/ev_range_pipeline.joblib
```

Make it feel like a system specification, not a statistic card farm.

---

# 33 — PAGE 4: INSIGHTS

Route:

```text
/insights
```

Purpose:

Show the plots and interpret what the model learned.

This page should be visually interesting.

---

# 34 — INSIGHTS PAGE: FEATURE IMPORTANCE

Use the existing feature-importance plot from:

```text
plots/
```

Do not replace it with a fake chart if the actual plot already exists.

Add:

```text
WHAT DRIVES RANGE?

battery_per_seat              49.99%
battery_capacity_kWh          34.03%
height_mm                      5.12%
fast_charging_power_kw_dc      3.48%
torque_per_100kwh              1.28%
```

and other documented feature contributions where present.

Interpret:

```text
Battery-per-seat and battery capacity together account for roughly 84%
of the model's total feature importance.
```

Do not call feature importance "causal influence".

It is model feature importance, not proof of physical causation.

---

# 35 — INSIGHTS PAGE: ACTUAL VS PREDICTED

Use the existing:

```text
model vs actual
```

plot from `plots/`.

Give it a strong section title:

```text
DO PREDICTIONS TRACK THE DATA?
```

Then:

```text
Actual range on one axis.
Predicted range on the other.

The closer points stay to the reference relationship,
the more closely the model follows the held-out observations.
```

Use the actual plot, not a newly fabricated example.

---

# 36 — INSIGHTS PAGE: MODEL COMPARISON

Use the existing model comparison image as well.

This page can contain three major visual modules:

```text
01 / MODEL COMPARISON
02 / ACTUAL VS PREDICTED
03 / FEATURE IMPORTANCE
```

But do not stack three full-width images with identical styling.

Vary the composition:

```text
large chart
↓
two-column chart + explanation
↓
large chart + annotation
```

This creates visual rhythm.

---

# 37 — INSIGHTS PAGE: ENGINEERING INTERPRETATION

Add short insights:

### Battery

Higher battery capacity strongly contributes to predicted range.

### Vehicle dimensions

Height contributes some predictive signal, plausibly reflecting the vehicle's physical/aerodynamic characteristics.

### Performance

Torque and fast-charging characteristics contribute additional signal.

Important:

Use cautious wording such as:

```text
contributes to model prediction
```

not:

```text
causes range loss
```

---

# 38 — OPTIONAL PAGE 5: METHOD / DATA

Only create this page if the content is substantial enough to justify it.

Route:

```text
/method
```

This can contain:

- dataset audit
- missing value strategy
- leakage prevention
- special cargo-volume cleanup
- preprocessing architecture
- limitations

Do not make this an excuse to create another massive wall of text.

---

# 39 — NAVIGATION

The navigation should now be:

```text
EV RANGE / ML

Home
Predictor
Model
Insights
```

Use the current page as an active state.

Do not use a hamburger menu on desktop.

On mobile, collapse cleanly.

---

# 40 — VISUAL SYSTEM

The redesigned UI should be much more visually intentional than the current version.

## Background

Use a mostly light neutral or warm-white background.

A dark page section may be used selectively.

Do not make the entire site black.

## Text

Use:

- almost-black for primary text
- muted gray for supporting text
- restrained accent for active states

## Borders

Prefer:

```text
1px solid subtle neutral
```

over huge shadows.

## Radius

Keep corners moderately restrained.

Avoid:

```text
24px–40px everywhere
```

A technical product should feel more precise.

---

# 41 — DESIGN LANGUAGE

Use the vocabulary of a technical instrument.

Examples:

```text
01 / PREDICTOR
02 / PERFORMANCE
03 / PIPELINE
04 / INTERPRETATION
05 / NOTES
```

Small uppercase labels can be used.

But do not turn every sentence into uppercase.

---

# 42 — TYPOGRAPHY

Use a strong modern sans serif such as:

```text
Inter
IBM Plex Sans
Manrope
Geist
```

Use a monospace typeface only for:

- numerical readouts
- metric values
- code-like technical labels

Do not use monospace for everything.

---

# 43 — AVOID THE "AI WEBSITE" LOOK

Absolutely avoid:

- purple-blue gradients
- rainbow gradients
- glowing green text
- animated circuit-board backgrounds
- floating glass cards
- giant AI brain illustrations
- generic futuristic electric car imagery
- excessive rounded corners
- huge shadows
- random blobs
- over-animated metric counters
- excessive blur
- decorative 3D objects
- "Powered by AI" badges
- fake confidence scores
- meaningless dashboards

The visual goal is:

```text
technical
credible
editorial
automotive
data-driven
```

---

# 44 — USE THE PLOTS AS VISUAL ANCHORS

The actual plots can give the site much more personality.

Do not hide them behind an "Analytics" button.

They are evidence.

Use them prominently on `/model` and `/insights`.

Where image dimensions permit, preserve readability.

Do not stretch plots beyond their useful aspect ratio.

---

# 45 — IMAGE PRESENTATION

For plot containers:

```text
background: slightly different neutral
border: subtle
padding: 20–28px
caption below
```

Do not put a huge shadow around every image.

A small source note can be:

```text
From project training/evaluation artifacts
```

Only use claims supported by the actual plot.

---

# 46 — HOME PAGE MOTION

Motion should be restrained.

Allowed:

- subtle page transitions
- button hover
- small result reveal
- chart entrance
- nav state transitions

Avoid:

- perpetual animations
- floating elements
- parallax everywhere
- cursor trails
- animated gradients
- bouncing cards
- loading screens that take attention away from the task

---

# 47 — PREDICTION INTERACTION

The interaction should feel immediate.

Sequence:

```text
User edits values
↓
Clicks Estimate Range
↓
Button changes to "Predicting..."
↓
Backend responds
↓
Result card updates
↓
Result number appears
↓
Input summary confirms what was received
```

Do not reload the page.

---

# 48 — PREDICTION ERROR HANDLING

Implement clear states:

## Validation error

Example:

```text
Battery capacity must be greater than 0.
```

## Backend error

```text
The prediction service could not complete this request.
Check that the model service is running.
```

## Unexpected error

```text
Something went wrong while generating the prediction.
```

Do not show Python stack traces to the user.

---

# 49 — LOADING STATE

Use an inline state:

```text
Predicting…
```

or:

```text
Running model…
```

No giant spinner.

No fake 2-second artificial delay.

Do not slow the application merely to make it feel "premium".

---

# 50 — RESULT HISTORY

Optional but useful.

After several predictions, show a small local-only history list:

```text
Recent predictions

Sedan / 77.4 kWh        482 km
SUV / 68.0 kWh          421 km
Compact / 40.0 kWh      289 km
```

This is particularly valuable for showing that different inputs can actually produce different predictions.

Important:

Do not store personal data on a server.

Use browser memory/localStorage only if implemented.

If the model genuinely outputs similar numbers, do not artificially spread the values.

---

# 51 — FRONTEND IMPLEMENTATION

Use:

```text
HTML5
CSS3
Vanilla JavaScript
```

Keep the code understandable.

Do not add React, Next.js, Tailwind, or TypeScript unless the existing project already depends on one of them and migrating would create more risk than value.

Do not rewrite the entire backend just for visual reasons.

---

# 52 — BACKEND IMPLEMENTATION

Use the existing Flask architecture where possible.

Required routes:

```text
GET /
GET /predictor
GET /model
GET /insights
POST /api/predict
```

If using templates:

```text
templates/
    home.html
    predictor.html
    model.html
    insights.html
```

Shared styling:

```text
static/css/
    base.css
    components.css
    pages.css
```

Shared JavaScript:

```text
static/js/
    predictor.js
```

Do not create an enormous single CSS file if it becomes difficult to maintain.

---

# 53 — MODEL LOADING

Load the Joblib pipeline once:

```python
pipeline = joblib.load("model/ev_range_pipeline.joblib")
```

Do not load it on every prediction request.

---

# 54 — FEATURE ENGINEERING LOCATION

The canonical feature-engineering logic should live in one Python function.

Example concept:

```python
def prepare_features(payload):
    ...
    return dataframe
```

Then:

```python
features = prepare_features(payload)
prediction = pipeline.predict(features)[0]
```

This prevents inconsistent feature calculations.

---

# 55 — DO NOT PREPROCESS IN JAVASCRIPT

The browser should collect user input.

The backend should:

1. validate,
2. normalize raw values,
3. create derived features,
4. construct the DataFrame,
5. pass it to the serialized pipeline,
6. return the prediction.

Do not duplicate ML preprocessing logic in JavaScript.

---

# 56 — API RESPONSE

Return at minimum:

```json
{
  "predicted_range_km": 482.31
}
```

Prefer returning a little context too:

```json
{
  "predicted_range_km": 482.31,
  "model": "Gradient Boosting Regressor"
}
```

Potentially:

```json
{
  "predicted_range_km": 482.31,
  "model": "Gradient Boosting Regressor",
  "received_input": {
    "battery_capacity_kWh": 77.4,
    "car_body_type": "SUV",
    "drivetrain": "RWD",
    "seats": 5
  }
}
```

Do not expose internal model objects.

---

# 57 — EXACT PREDICTION DEBUGGING REQUIREMENT

Before declaring the app finished, run a test table similar to:

| Case | Battery | Seats | Dimensions | Prediction |
|---|---:|---:|---|---:|
| A | 35 | 4 | small | ??? |
| B | 77 | 5 | medium | ??? |
| C | 110 | 7 | large | ??? |

The outputs must be actual model outputs.

If all predictions are identical or nearly identical:

1. inspect the frontend payload,
2. inspect backend request values,
3. inspect engineered DataFrame,
4. inspect pipeline inputs,
5. inspect prediction.

Continue until the root cause is understood.

Do not simply modify UI display logic.

---

# 58 — MODEL SCHEMA CHECK

At development time, inspect the pipeline:

```python
print(type(pipeline))
print(getattr(pipeline, "feature_names_in_", None))
```

If the pipeline contains a `ColumnTransformer`, inspect its configured columns.

The goal is to determine exactly which raw columns the model expects.

Do not infer the schema only from the UI.

---

# 59 — PREDICTION SANITY CHECK

A sanity check should compare predictions for controlled changes.

For example:

### Change only battery capacity

Hold other values constant.

Test:

```text
50 kWh
70 kWh
90 kWh
```

Observe whether the prediction changes.

Then:

### Change only seats

Test:

```text
4
5
7
```

Then:

### Change dimensions

Hold everything else fixed while changing dimensions.

This does not prove model correctness, but it reveals whether inputs are actually flowing through.

---

# 60 — IMPORTANT: DO NOT OVERPROMISE PHYSICAL INTERPRETATION

The project uses machine learning on specification data.

Feature importance tells us which features were important to the trained model.

It does not prove:

```text
feature X physically causes range change Y
```

Use language such as:

```text
strong predictive signal
model importance
contributes to the prediction
```

---

# 61 — LIMITATIONS

Keep a visible but compact limitations section on `/model` or `/method`.

Use the project documentation accurately:

### Rated vs real-world range

The target represents official rated range. Real-world range can vary with:

- ambient temperature
- HVAC
- driving behavior
- terrain
- other conditions

### Missing cell metadata

`number_of_cells` is missing in 42.3% of vehicles and is handled with imputation plus a missingness flag.

### Cargo volume normalization

Some values are recorded as banana boxes and converted using:

```text
1 banana box = 52 L
```

Do not make the banana-box detail the star of the website.

---

# 62 — RESPONSIVE DESIGN

Test at:

```text
1440
1280
1024
768
430
390
360
```

Desktop:

- wide predictor layout
- large chart area
- editorial two-column sections

Tablet:

- reduce side padding
- collapse some two-column sections

Mobile:

- one column
- navigation collapses
- form groups stack
- result panel appears early
- buttons become full width
- charts remain readable
- no horizontal scrolling

---

# 63 — MOBILE PREDICTOR PRIORITY

On mobile:

```text
page heading
↓
result / status
↓
prediction form
↓
details
```

The user should not have to scroll through huge explanatory text before reaching the form.

---

# 64 — ACCESSIBILITY

Include:

- semantic HTML
- proper labels
- keyboard access
- visible focus state
- sufficient contrast
- `aria-live` result region
- meaningful button text
- error messages tied to inputs

Respect:

```css
@media (prefers-reduced-motion: reduce)
```

---

# 65 — PERFORMANCE

Keep the app lightweight.

Avoid:

- loading huge JS libraries for simple tasks
- multiple animation frameworks
- unnecessary network requests
- unnecessary image duplication

The existing plots are useful, so optimize their display rather than removing them.

---

# 66 — FILE / ROUTING ORGANIZATION

Recommended target:

```text
ev-range-web/
│
├── app.py
├── requirements.txt
│
├── model/
│   └── ev_range_pipeline.joblib
│
├── plots/
│   ├── model_comparison.*
│   ├── actual_vs_predicted.*
│   ├── feature_importance.*
│   └── other project plots...
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── predictor.html
│   ├── model.html
│   └── insights.html
│
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── components.css
│   │   └── pages.css
│   │
│   └── js/
│       └── predictor.js
│
└── scripts/
    └── test_predictions.py
```

Adapt to the existing project rather than unnecessarily restructuring everything.

---

# 67 — SHARED DESIGN COMPONENTS

Build reusable visual patterns:

### Section marker

```text
01 / PREDICTOR
```

### Metric

```text
98.13%
R²
```

### Technical label

```text
MODEL
Gradient Boosting Regressor
```

### Plot frame

```text
TITLE
chart
short interpretation
```

### Input group

```text
BATTERY
field field
```

This creates consistency without turning every element into a card.

---

# 68 — COLOR SYSTEM

Use a restrained palette.

Example direction:

```text
Background:
#F5F4F0 or similar warm neutral

Primary:
#161616

Muted:
#6F6F6A

Border:
#D8D7D1

Accent:
one restrained green / teal / electric tone
```

Do not copy these exact colors blindly.

The main idea is:

```text
neutral foundation
+
one strong accent
+
dark technical text
```

No rainbow.

---

# 69 — DARK SECTION USAGE

A dark section can work well for:

```text
Model Performance
```

or:

```text
Engineering Notes
```

But do not make every section dark.

Use contrast intentionally.

---

# 70 — SPACING

Use consistent spacing tokens.

Example:

```text
8
12
16
24
32
48
64
96
```

Do not randomly use huge gaps.

The current design's problem is not that it lacks whitespace; it lacks intentional composition.

Whitespace should separate concepts, not create empty fields.

---

# 71 — HERO SIZE

Do not create a hero that takes the entire first screen.

The user should reach meaningful content quickly.

Target:

```text
hero ≈ 60–80vh maximum
```

depending on viewport.

The main predictor should be accessible immediately.

---

# 72 — HEADER BEHAVIOR

Header should be:

- compact
- sticky only if useful
- not oversized

Use a subtle bottom border.

No giant glass blur header.

---

# 73 — FOOTER

Keep it simple:

```text
EV RANGE / MACHINE LEARNING

Gradient Boosting Regressor
Scikit-Learn · Flask · Joblib

Engineering-focused ML project
```

No fake company logo.

No fake copyright entity.

No unnecessary social links.

---

# 74 — COPY STYLE

Use direct technical language.

Good:

```text
Estimate range from engineering specifications.
```

Bad:

```text
Unlock the power of next-generation AI.
```

Good:

```text
Evaluated on 96 held-out vehicles.
```

Bad:

```text
98%+ accuracy that changes the game.
```

Do not call R² "accuracy".

---

# 75 — NO FAKE CONFIDENCE SCORE

Do not display:

```text
Confidence: 97%
```

unless the actual model supports a statistically valid confidence estimate.

The project documentation does not provide one.

Likewise do not invent:

```text
prediction interval
probability
certainty meter
```

---

# 76 — NO FAKE "REAL-TIME" LABEL

The system is not consuming live vehicle telemetry.

Do not say:

```text
real-time vehicle intelligence
```

A better phrase is:

```text
Instant prediction from supplied specifications.
```

---

# 77 — NO FAKE DATA

Do not add:

- fake EV manufacturers
- fake vehicles
- fake user reviews
- fake benchmark datasets
- fake deployment counts
- fake accuracy comparisons
- fake production claims

Only use project-supported information.

---

# 78 — PLOT FILE HANDLING

Determine the plot file formats actually present.

If they are PNG/JPG/WebP:

copy or reference them appropriately.

If they are SVG:

use them carefully so they remain crisp.

Do not convert them to low-resolution screenshots unnecessarily.

Do not alter plot content just to match UI colors unless a derivative copy is clearly appropriate.

---

# 79 — IF PLOTS LOOK VISUALLY INCONSISTENT

Do not redraw the plots automatically.

First assess whether the actual project plots are readable.

If their styling clashes badly with the redesigned page, place them inside a consistent frame and provide clean captions.

Preserve their informational integrity.

---

# 80 — OPTIONAL INTERACTIVE ENHANCEMENT

On `/insights`, a plot may have a simple "expand" action.

For example:

```text
View larger
```

This is acceptable.

Do not build a complicated analytics application around static plots.

---

# 81 — PAGE TRANSITIONS

Prefer actual routes:

```text
Home
Predictor
Model
Insights
```

Do not simulate pages by creating one giant DOM where all sections are hidden and shown.

Separate pages make the project feel intentional and improve information architecture.

---

# 82 — KEEP HOME DIFFERENT FROM MODEL

Home:

```text
What is this?
Why use it?
Try it.
```

Model:

```text
How was it built?
How well did it perform?
What was selected?
```

Insights:

```text
What does the model learn?
What do the plots show?
```

Predictor:

```text
Give inputs.
Get prediction.
```

This distinction must be obvious.

---

# 83 — DESIGN REVIEW AGAINST THE CURRENT VERSION

The current version should NOT survive unchanged patterns such as:

- huge vertical blank spaces
- section after section that looks like plain documentation
- repeated same-width cards
- generic metric tiles everywhere
- charts simply dropped into the page
- overly small content inside huge containers
- weak page differentiation
- one giant scrolling experience

The redesign should have a noticeably different visual composition.

---

# 84 — EXPECTED FIRST IMPRESSION

When someone opens the website, they should think:

> "This looks like a real engineering ML project."

not:

> "This looks like an AI website template."

The design should be mature enough to sit in an ML portfolio.

---

# 85 — EXPECTED PREDICTOR EXPERIENCE

A user should be able to:

1. Open Predictor.
2. Understand what each field means.
3. Load an example.
4. Change battery / dimensions / performance.
5. Click Predict.
6. See a prediction without page reload.
7. See which key inputs were received.
8. Try another specification set.
9. Notice that the prediction responds to meaningful changes when the model does.

---

# 86 — FINAL TEST PLAN

Before delivery, perform all of these.

## Functional

```text
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

Test:

```text
/
 /predictor
 /model
 /insights
```

Confirm no 404s.

---

## Prediction

Run at least five distinct prediction inputs.

Example sequence:

```text
35 kWh
55 kWh
77 kWh
95 kWh
110 kWh
```

with other sensible fields.

Record outputs.

Then change dimensions substantially.

Record outputs.

Then change seats / torque / drivetrain where applicable.

Record outputs.

---

# 87 — PREDICTION BUG ACCEPTANCE CRITERIA

The implementation is NOT complete if:

- the frontend sends the same payload every time,
- backend receives stale values,
- engineered features are unchanged when inputs change,
- model DataFrame is constant,
- prediction is hard-coded,
- output is changed with random noise,
- output is merely a frontend formula unrelated to the trained model.

The implementation IS complete when:

```text
different input
→ different actual payload
→ different engineered representation where appropriate
→ actual model inference
→ returned model output
```

Even if the model sometimes produces similar outputs, the data path must be demonstrably correct.

---

# 88 — SECURITY / ROBUSTNESS

Do not allow arbitrary file paths, Python expressions, or model selection from the frontend.

The browser should only submit expected JSON fields.

Never let the client choose:

```text
which .joblib to load
```

The server chooses the model.

---

# 89 — PRODUCTION CLEANUP

After debugging:

Remove:

- temporary debug endpoints
- noisy console logs
- test-only UI
- hard-coded sample outputs
- comments that refer to temporary hacks

Keep:

- useful error handling
- maintainable code
- prediction validation
- the controlled prediction test script

---

# 90 — FINAL DELIVERABLE

Deliver a working multi-page Flask website with:

```text
Home
Predictor
Model
Insights
```

using the real model and real plots.

The final experience should be:

```text
clean
technical
credible
interactive
restrained
automotive
data-driven
```

It should NOT be:

```text
generic
neon
over-animated
card-heavy
AI-template-looking
```

---

# 91 — MOST IMPORTANT PRIORITIES, IN ORDER

When tradeoffs appear, follow this order:

### 1. Prediction correctness

The model must receive the user's actual inputs.

### 2. Multi-page information architecture

Do not force the entire project into one long page.

### 3. Strong predictor UX

The input → prediction flow is the core feature.

### 4. Actual project evidence

Use the existing plots and documented metrics.

### 5. Visual quality

Make the design polished, distinctive and restrained.

### 6. Animation and decoration

Only after everything above is correct.

---

# 92 — FINAL DESIGN DIRECTIVE

Do not try to make the project impressive by adding more things.

Make it impressive by making the existing things **clearer, better composed, and more credible**.

The strongest visual idea should be:

```text
engineering data → machine learning → predicted range
```

Everything on the website should support that story.

