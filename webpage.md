# EV Range Prediction — Webpage Build Specification

## 0. What you are building

Build a **production-looking single-page web application** for an Electric Vehicle (EV) Range Prediction ML project.

The page should let a user enter EV technical specifications, submit them to the trained model, and receive an estimated driving range in kilometers.

This is **not** supposed to look like an "AI SaaS template", futuristic neon dashboard, or a generic ChatGPT-generated portfolio page.

The source project is a reproducible, leak-free regression pipeline trained on 478 EV models. The selected final model is a tuned **Gradient Boosting Regressor** with:

- R²: **0.9813**
- MAE: **10.82 km**
- RMSE: **14.08 km**

The complete preprocessing + feature engineering + model pipeline is stored as:

`model/ev_range_pipeline.joblib`

Source-derived project details must be preserved accurately. Do not invent model metrics, datasets, features, APIs, or claims.

---

# 1. Recommended technology stack

Use a deliberately small and reliable stack.

## Frontend

- HTML5
- CSS3
- Vanilla JavaScript
- Fetch API
- Chart.js only where a chart genuinely improves the page
- No React
- No Next.js
- No TypeScript
- No Tailwind
- No large UI component library
- No unnecessary animation library

## Backend

- Python 3
- Flask
- Flask-CORS only if frontend/backend are served separately during development
- pandas
- scikit-learn
- joblib

## Model

Load:

`model/ev_range_pipeline.joblib`

The backend must use the **serialized end-to-end pipeline** rather than rebuilding preprocessing manually.

This is important because the original project stores preprocessing, transformations, feature engineering-compatible inputs, and the trained Gradient Boosting model together.

## Development structure

Use this structure:

```text
ev-range-web/
│
├── app.py
├── requirements.txt
├── model/
│   └── ev_range_pipeline.joblib
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── README.md
```

Keep the frontend and backend simple enough that the project can run locally without complicated tooling.

---

# 2. Primary product goal

The first screen should immediately communicate:

> **Predict EV range from engineering specifications.**

The user should understand within a few seconds:

1. What the model predicts.
2. What inputs it uses.
3. What the prediction represents.
4. How accurate the final model is.
5. That this is based on specification-sheet data rather than real-time driving telemetry.

The prediction form is the main product interaction.

Do not bury it below a huge hero section.

---

# 3. Critical visual direction

## The most important design rule

**Do not make it look AI-generated.**

Avoid the common visual patterns that instantly make websites look machine-generated:

- Purple/blue gradient backgrounds
- Giant glowing text
- Excessive glassmorphism
- Floating neon cards
- Gradient borders everywhere
- Huge rounded rectangles
- Excessive shadows
- Random decorative blobs
- Overuse of emojis
- Generic robot/AI imagery
- "Powered by AI" badges
- Fake futuristic terminology
- Excessive motion
- 3D floating dashboards
- Stock illustrations of electric cars
- Huge centered headings occupying half the viewport

The page should feel like it was designed by someone who understands **automotive engineering + data science**.

---

# 4. Visual personality

Use a restrained engineering / automotive data-visualization aesthetic.

Think:

- automotive instrument cluster
- technical specification sheet
- modern engineering workstation
- clean EV manufacturer configurator
- scientific dashboard
- data visualization interface

But do not copy a specific company's branding.

The interface should feel **quietly technical**, not flashy.

## Suggested palette

Use a mostly neutral foundation:

- warm/off-white page background
- near-black text
- dark graphite panels
- muted gray borders
- one restrained electric accent color

A single accent may be used for:

- prediction value
- active input
- primary CTA
- selected chart series
- status indicator

Do not use multiple competing accent colors.

---

# 5. Typography

Use a professional sans-serif.

Possible choices:

- Inter
- IBM Plex Sans
- Manrope
- Geist

For technical numbers and model metrics, a monospace font such as:

- IBM Plex Mono
- JetBrains Mono

can be used selectively.

Do not make every element monospace.

Hierarchy should come from:

- size
- weight
- whitespace
- contrast

not from decorative effects.

---

# 6. Layout philosophy

The page should use a **strong editorial grid** rather than a random card grid.

Recommended order:

```text
Header
↓
Compact Hero / Project Introduction
↓
Prediction Workspace
    ├── Input form
    └── Prediction result
↓
Model Performance
↓
How the Model Works
↓
Feature Importance
↓
Data Quality / Leakage Control
↓
Limitations
↓
Footer
```

The prediction workspace is the visual center of the page.

---

# 7. Header

Keep the header compact.

Left:

**EV RANGE / ML MODEL**

Small secondary label:

`Engineering Specification Predictor`

Right navigation:

- Predictor
- Performance
- Method
- Limitations

Navigation should scroll to sections.

Do not create a giant navigation bar.

On mobile, collapse navigation into a simple menu button.

---

# 8. Hero section

Do not make this a conventional marketing hero.

Use a compact, editorial hero.

Possible structure:

```text
EV RANGE PREDICTION

From specification sheet → estimated driving range

A machine learning regression model trained on 478 EV models,
using battery, dimensions, drivetrain and performance specifications.

[Open Predictor]
```

Alongside the text, show a restrained technical visual.

For example:

```text
RANGE_KM

393.18
dataset mean

135 — 685 km
observed target range
```

This is better than using a large stock EV photograph.

---

# 9. Prediction workspace

This is the most important section.

Use a two-column desktop layout.

```text
┌────────────────────────────────────────────────────────────┐
│  VEHICLE SPECIFICATIONS             PREDICTED RANGE         │
│                                                            │
│  Battery capacity      [ 77.4     ]       487 km           │
│  Top speed              [ 180      ]       estimated        │
│  Torque                 [ 350      ]                        │
│  Seats                  [ 5        ]       ± context        │
│  Length                 [ 4635     ]                        │
│  Width                  [ 1890     ]                        │
│  Height                 [ 1605     ]                        │
│  ...                                                        │
│                                                            │
│  [ Predict Range ]                     Model: Gradient     │
│                                      Boosting Regressor     │
└────────────────────────────────────────────────────────────┘
```

The form should feel like entering data into a real engineering tool.

---

# 10. Form fields

The page must support the raw prediction inputs represented by the project.

Use clear labels with units.

Recommended fields:

### Performance

- Top Speed — km/h
- Acceleration 0–100 — seconds
- Torque — Nm
- Fast Charging Power — kW DC
- Towing Capacity — kg

### Battery

- Battery Capacity — kWh
- Number of Cells
- Seats

### Dimensions

- Length — mm
- Width — mm
- Height — mm
- Cargo Volume — L

### Configuration

- Drivetrain
  - FWD
  - RWD
  - AWD

- Segment
  - use values appropriate to the dataset
  - include a safe default

- Body Type
  - SUV
  - Sedan
  - Hatchback
  - or other dataset-supported values

### Missing cells

Include a small checkbox or toggle:

`Battery cell count unavailable`

This must map to:

`cells_missing_flag`

---

# 11. Important implementation detail: derived features

The model documentation says the project created these domain-specific features:

```text
footprint_m2
volume_m3
battery_per_seat
torque_per_100kwh
segment_group
```

The frontend should **not ask the user to enter these derived fields manually**.

Calculate them in the backend before prediction.

Formulas:

```text
footprint_m2 =
(length_mm / 1000) * (width_mm / 1000)

volume_m3 =
footprint_m2 * (height_mm / 1000)

battery_per_seat =
battery_capacity_kWh / seats

torque_per_100kwh =
(torque_nm / battery_capacity_kWh) * 100

segment_group =
prefix / group derived from segment
```

Do not duplicate these calculations in several locations.

Create one backend feature-engineering function.

Validate inputs before calculation.

Handle division-by-zero safely.

---

# 12. Data leakage warning

This deserves a visible but compact explanation.

The project intentionally excludes:

`efficiency_wh_per_km`

because range is approximately related to:

```text
range ≈ battery capacity / efficiency
```

Including efficiency would create a form of target leakage.

Show this as a small technical note:

> Efficiency is intentionally not an input. It is excluded to prevent target leakage.

This is a strong ML engineering detail and should be visible somewhere on the page.

---

# 13. Prediction result design

After submission, do not just show:

`487.23 km`

Make the result feel useful.

Example:

```text
ESTIMATED RANGE

487 km

Based on supplied vehicle specifications

Model
Gradient Boosting Regressor

Test MAE
10.82 km

Test RMSE
14.08 km
```

The range number should be visually dominant.

Use a subtle engineering-style gauge or horizontal scale if useful, but do NOT turn the page into a sci-fi speedometer.

---

# 14. Prediction states

The UI must handle:

### Initial state

Show:

`Enter specifications to estimate range.`

### Loading

Show:

`Running model...`

Use a small inline loader.

Do not use a full-screen artificial loading animation.

### Success

Show predicted range and model context.

### Invalid input

Display specific field errors.

Example:

`Battery capacity must be greater than 0.`

### Backend unavailable

Show:

`Prediction service is unavailable. Start the Flask server and try again.`

Do not expose raw Python traceback to the user.

---

# 15. Model performance section

Create a clean evidence-focused section.

Title:

**MODEL PERFORMANCE**

Intro:

`The final model was evaluated on 96 held-out EVs.`

Show three metrics prominently:

```text
98.13%
R²

10.82 km
MAE

14.08 km
RMSE
```

Then show the comparison:

| Model | Test RMSE | Test MAE | R² |
|---|---:|---:|---:|
| Ridge | 17.61 km | 13.96 km | 0.9707 |
| Gradient Boosting | 14.08 km | 10.82 km | 0.98126 |

Make the Gradient Boosting row visually stronger.

Do not fabricate a full leaderboard for test performance.

The source only provides these final held-out values for Ridge and Gradient Boosting.

---

# 16. Cross-validation section

The source project benchmarked six model families with 5-fold CV.

Display this information accurately:

| Model | 5-Fold CV Mean RMSE |
|---|---:|
| Ridge Regression | 19.57 km |
| Gradient Boosting Regressor | 22.53 km |
| Lasso Regression | 24.85 km |
| XGBoost Regressor | 24.88 km |
| Random Forest Regressor | 24.94 km |
| Linear Regression | 33.07 km |

Important:

The source says Ridge had the lower CV RMSE, while Gradient Boosting became the final winner on the held-out test set after tuning.

Do NOT rewrite this as "Gradient Boosting won every benchmark."

That would be inaccurate.

A small explanatory note should say:

> Ridge was strongest in the initial CV benchmark, but the tuned Gradient Boosting model produced the best final held-out test performance.

---

# 17. Feature importance

Create a restrained horizontal bar chart.

Do not use a giant pie chart.

Top features documented by the project:

```text
battery_per_seat              49.99%
battery_capacity_kWh          34.03%
height_mm                      5.12%
fast_charging_power_kw_dc      3.48%
torque_per_100kwh              1.28%
car_body_type_SUV              0.96%
car_body_type_Sedan            0.78%
```

Highlight the first two features.

Add:

`Battery-per-seat + battery capacity account for ~84% of model feature importance.`

Use a horizontal bar chart with a restrained palette.

---

# 18. "How it works" section

Show the ML pipeline visually.

Use a clean horizontal or responsive flow:

```text
RAW SPECIFICATIONS
        ↓
FEATURE ENGINEERING
        ↓
COLUMN TRANSFORMER
   ┌───────────────┐
   │ numeric       │ → median imputation → scaling
   │ categorical   │ → most-frequent   → one-hot encoding
   └───────────────┘
        ↓
GRADIENT BOOSTING
        ↓
PREDICTED RANGE
```

This section should make the project look technically credible.

Avoid generic AI diagrams with glowing nodes.

---

# 19. Reproducibility section

Show:

```text
TRAIN / TEST SPLIT
80 / 20

TRAINING SAMPLES
382

TEST SAMPLES
96

RANDOM SEED
42

MODEL ARTIFACT
model/ev_range_pipeline.joblib
```

The random seed is `42`.

The split is 382 training / 96 testing.

---

# 20. Data audit section

Present concise cards or a technical table.

Important source-derived facts:

- 478 total EV rows
- 22 initial attributes
- range_km target
- mean target: 393.18 km
- target range: 135–685 km
- number_of_cells missing: 202 / 478 = 42.3%
- towing_capacity_kg missing: 26
- torque_nm missing: 7
- fast_charging_power_kw_dc missing: 1
- cargo_volume_l missing: 1

Do not overwhelm the page with every raw data-cleaning detail.

The point is to show that data quality was considered.

---

# 21. Special data-cleaning note

The dataset contains some cargo volume entries represented as:

`"10 Banana Boxes"`

The project converts these using:

```text
1 Banana Box = 52 L
```

Present this as a small "dataset cleanup" technical detail.

Do not make this a major visual element.

It is an interesting implementation detail, not a selling point.

---

# 22. Limitations section

This should NOT be hidden.

Show a compact technical section titled:

**WHAT THIS MODEL DOES NOT KNOW**

Include:

### Real-world driving

The prediction is based on specification-sheet data and rated range. Real driving conditions can differ because of temperature, HVAC use, driving behavior, terrain, and other factors.

### Battery cell metadata

`number_of_cells` is missing for 42.3% of vehicles. The pipeline handles this using imputation plus a missingness flag, but richer battery metadata could improve the model.

### Cargo volume

Some cargo values require empirical normalization.

Do not claim that the prediction is a guaranteed real-world range.

---

# 23. Responsive behavior

The site must work properly at:

- 1440px desktop
- 1280px laptop
- 1024px tablet
- 768px tablet
- 390px mobile
- 360px mobile

Desktop:

- two-column predictor layout
- generous whitespace
- charts side-by-side where useful

Mobile:

- one column
- sticky or easy-to-reach Predict button
- inputs full width
- metrics stack naturally
- charts remain readable
- no horizontal scrolling

Never shrink desktop content until it becomes unreadable.

Reflow it.

---

# 24. Backend API

Create:

`POST /api/predict`

Example request:

```json
{
  "top_speed_kmh": 180,
  "battery_capacity_kWh": 77.4,
  "number_of_cells": 384,
  "torque_nm": 350,
  "acceleration_0_100_s": 7.3,
  "fast_charging_power_kw_dc": 233,
  "towing_capacity_kg": 1600,
  "seats": 5,
  "length_mm": 4635,
  "width_mm": 1890,
  "height_mm": 1605,
  "cargo_volume_l": 520,
  "drivetrain": "RWD",
  "segment": "JC - Medium",
  "car_body_type": "SUV",
  "cells_missing_flag": 0
}
```

Example response:

```json
{
  "predicted_range_km": 487.32
}
```

The actual response value must come from the loaded Joblib model.

Do not hard-code `487.32`.

---

# 25. Backend validation

Validate:

- required fields are present
- numeric values are numeric
- battery capacity > 0
- seats > 0
- dimensions > 0
- charging power >= 0
- torque can be 0 but not negative unless dataset permits it
- cargo volume is valid
- categorical values are strings

Return HTTP 400 for invalid user input.

Return HTTP 500 for unexpected model/server errors.

Log server-side errors, but return a clean error message to the browser.

---

# 26. CORS / serving

Preferred development setup:

Serve the frontend directly through Flask using:

```text
templates/index.html
static/css/style.css
static/js/app.js
```

Then frontend and API share the same origin.

This avoids unnecessary CORS problems.

The website should run with:

```bash
python app.py
```

and open at:

```text
http://127.0.0.1:5000
```

---

# 27. Flask behavior

At minimum implement:

```text
GET /
POST /api/predict
```

`GET /` renders the page.

`POST /api/predict` receives JSON and returns JSON.

Load the model once at application startup:

```python
pipeline = joblib.load("model/ev_range_pipeline.joblib")
```

Do NOT load the model on every request.

---

# 28. Accessibility

The UI should have:

- semantic HTML
- `<label>` elements for all form fields
- keyboard-accessible controls
- visible focus states
- sufficient color contrast
- ARIA live region for prediction results
- buttons with meaningful text
- no information conveyed by color alone

Do not sacrifice accessibility for visual effects.

---

# 29. Animation rules

Animation must be subtle.

Allowed:

- 150–250ms hover transitions
- small result reveal
- progress bars animating once
- chart entrance animation
- subtle nav underline

Avoid:

- perpetual background animation
- floating cards
- parallax overload
- cursor-following effects
- bouncing numbers
- spinning 3D EVs
- animated gradients
- excessive scroll animations

The site should still feel good when animations are disabled.

Respect:

```css
@media (prefers-reduced-motion: reduce)
```

---

# 30. Microcopy

Use technical and human wording.

Good:

- `Estimate Range`
- `Vehicle Specifications`
- `Model Performance`
- `Feature Importance`
- `Held-Out Test Set`
- `Leakage Control`
- `Engineering Notes`

Avoid:

- `Unlock AI Power`
- `Next-Gen Intelligence`
- `Revolutionary AI`
- `Powered by cutting-edge AI`
- `Experience the future`
- `Supercharge your insights`

This wording is a major part of making the website feel authentic.

---

# 31. Visual hierarchy rules

The page must have a clear hierarchy:

### Level 1
Predicted range

### Level 2
Prediction form + section titles

### Level 3
Model metrics

### Level 4
Technical explanations

### Level 5
Supporting metadata

Do not make every card equally prominent.

---

# 32. Cards

Use cards sparingly.

A card is appropriate when it groups genuinely related information.

Avoid putting every paragraph in its own card.

Recommended:

- one main prediction workspace
- one metrics block
- one model comparison block
- one feature importance visual
- one pipeline visual
- one limitations block

A flat editorial layout can be mixed with cards.

---

# 33. Icons

Use icons only when they improve scanning.

Possible categories:

- battery
- speed
- dimensions
- drivetrain
- seats
- charging

Use a consistent icon set.

Do not use emoji icons.

---

# 34. Charts

Use charts only for data that benefits from visualization.

Recommended:

1. Horizontal feature-importance bar chart.
2. Optional target range distribution / scale visualization.

Do not create a chart for every metric.

No fake charts.

All chart values must come from the project data/specification above.

---

# 35. Design details that will make it feel hand-designed

Pay attention to:

- slightly irregular but deliberate spacing
- strong alignment
- section numbers such as `01`, `02`, `03`
- small uppercase labels
- restrained dividers
- technical unit labels
- consistent decimal formatting
- intentional whitespace
- concise annotations
- asymmetric composition where useful
- a mix of dense and sparse sections

For example:

```text
01 / PREDICTOR
02 / PERFORMANCE
03 / PIPELINE
04 / INTERPRETATION
05 / LIMITATIONS
```

This creates an engineering-document character without looking like a PowerPoint.

---

# 36. What NOT to do

Never:

- invent additional model metrics
- claim real-world accuracy that was not measured
- say the model is production-certified
- say the model predicts exact range
- add fake confidence intervals
- create made-up EV brands
- show fake predictions that look like real measured results
- hard-code a result and pretend it came from the model
- expose the Joblib model to the browser
- rebuild preprocessing inconsistently in JavaScript
- manually scale inputs on the frontend
- rely on a CDN for core app functionality if a local asset is practical
- add unnecessary authentication
- add a database unless a real requirement appears
- turn it into a user account platform
- create a dashboard full of unrelated analytics

---

# 37. Quality standard

Before considering the page complete, verify all of the following.

## Functional

- Flask starts without errors.
- `/` loads.
- `/api/predict` works.
- Valid form data returns a prediction.
- Invalid data returns a useful 400 error.
- The Joblib pipeline loads successfully.
- The prediction uses the real model.
- Derived features are calculated correctly.
- No console errors.
- No broken assets.
- Mobile layout works.

## ML integrity

- Efficiency is not accepted as a prediction feature.
- Identifier/metadata fields are not added as predictive inputs.
- The serialized pipeline is used.
- No preprocessing is performed incorrectly in the browser.
- Model metrics match the project documentation.

## Design

- The first viewport clearly communicates what the model does.
- Prediction is easy to find.
- Typography is consistent.
- Spacing is intentional.
- Charts are readable.
- No visual clutter.
- No excessive gradients.
- No neon sci-fi styling.
- No generic AI imagery.
- The page looks credible to an ML engineer or materials/automotive engineering student.

---

# 38. Suggested page copy

## Hero

**EV RANGE PREDICTION**

`Estimate electric vehicle driving range from engineering specifications.`

`A reproducible regression pipeline trained on 478 EV models.`

CTA:

`Open Predictor`

---

## Predictor

**01 / PREDICTOR**

**Vehicle specifications**

`Enter the vehicle's technical specifications to estimate rated range.`

Button:

**Estimate Range**

Result heading:

**Predicted range**

---

## Performance

**02 / MODEL PERFORMANCE**

`Held-out evaluation on 96 unseen vehicles.`

Metrics:

`98.13% R²`
`10.82 km MAE`
`14.08 km RMSE`

---

## Method

**03 / HOW THE MODEL WORKS**

`Raw specifications are cleaned, transformed and passed through one reproducible preprocessing + modeling pipeline.`

---

## Interpretation

**04 / WHAT DRIVES THE PREDICTION**

`Battery-related features dominate the model's predictive importance, with battery-per-seat and battery capacity together contributing roughly 84% of total feature importance.`

---

## Limitations

**05 / ENGINEERING NOTES**

`This model predicts from static specification data. It does not observe weather, traffic, terrain, HVAC load or driving behavior.`

---

# 39. Recommended footer

Keep it understated.

Example:

```text
EV RANGE / MACHINE LEARNING PROJECT

Gradient Boosting Regressor
Scikit-Learn · Flask · Joblib

Built as an engineering-focused ML demonstration.
```

Do not add fake company information.

---

# 40. Final instruction to the coding agent

Treat this specification as a **design system + implementation contract**, not merely a content outline.

The final result should feel like a carefully designed technical product.

The strongest differentiator should be:

**clarity + engineering credibility + restraint.**

The UI should communicate that an actual ML pipeline exists behind the page.

Do not compensate for missing visual quality with gradients, animations, or decorative effects.

Before finishing, test the entire flow:

```text
Browser
  ↓
HTML form
  ↓
JavaScript validation
  ↓
POST /api/predict
  ↓
Flask
  ↓
feature engineering
  ↓
Joblib pipeline
  ↓
prediction
  ↓
JSON response
  ↓
result UI
```

If any part of that chain is simulated instead of actually working, the implementation is incomplete.
