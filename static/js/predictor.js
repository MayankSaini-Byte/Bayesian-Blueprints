/* ==========================================================================
   Predictor JS — Client-side interaction logic
   ========================================================================== */

(function () {
  "use strict";

  const form           = document.getElementById("predict-form");
  const btnPredict     = document.getElementById("btn-predict");
  const btnLoadExample = document.getElementById("btn-load-example");
  const resultPanel    = document.getElementById("result-panel");
  const stateInitial   = document.getElementById("result-initial");
  const stateLoading   = document.getElementById("result-loading");
  const stateSuccess   = document.getElementById("result-success");
  const stateError     = document.getElementById("result-error");
  const errorMsg       = document.getElementById("result-error-msg");
  const resultNumber   = document.getElementById("result-number");
  const rangeBarFill   = document.getElementById("range-bar-fill");
  const rangeBarMark   = document.getElementById("range-bar-marker");
  const cellsMissing   = document.getElementById("cells_missing_flag");
  const cellsInput     = document.getElementById("number_of_cells");
  const inputSummary   = document.getElementById("input-summary");
  const inputSummaryG  = document.getElementById("input-summary-grid");
  const historyPanel   = document.getElementById("history-panel");
  const historyList    = document.getElementById("history-list");

  const RANGE_MIN = 135;
  const RANGE_MAX = 685;

  // Example vehicle specs (Typical mid-size EV)
  const EXAMPLE_SPECS = {
    battery_capacity_kWh: 77.4,
    number_of_cells: 384,
    cells_missing_flag: false,
    seats: 5,
    top_speed_kmh: 180,
    acceleration_0_100_s: 7.3,
    torque_nm: 350,
    fast_charging_power_kw_dc: 233,
    towing_capacity_kg: 1600,
    length_mm: 4635,
    width_mm: 1890,
    height_mm: 1605,
    cargo_volume_l: 520,
    drivetrain: "RWD",
    segment: "JC - Medium",
    car_body_type: "SUV"
  };

  // Toggle cell count input
  if (cellsMissing) {
    cellsMissing.addEventListener("change", function () {
      cellsInput.disabled = this.checked;
      if (this.checked) cellsInput.value = "";
    });
  }

  // Load example button
  if (btnLoadExample) {
    btnLoadExample.addEventListener("click", function () {
      Object.keys(EXAMPLE_SPECS).forEach(function (key) {
        const el = form.elements[key];
        if (!el) return;
        if (el.type === "checkbox") {
          el.checked = EXAMPLE_SPECS[key];
          if (key === "cells_missing_flag") {
            cellsInput.disabled = el.checked;
          }
        } else {
          el.value = EXAMPLE_SPECS[key];
        }
      });
      clearValidationErrors();
    });
  }

  function showState(state) {
    [stateInitial, stateLoading, stateSuccess, stateError].forEach(function (el) {
      if (el) el.classList.add("hidden");
    });
    if (state) state.classList.remove("hidden");
  }

  function clearValidationErrors() {
    form.querySelectorAll("input, select").forEach(function (el) {
      el.classList.remove("input-error");
    });
  }

  function validateForm() {
    clearValidationErrors();
    const errors = [];
    const required = [
      ["battery_capacity_kWh", "Battery capacity"],
      ["top_speed_kmh", "Top speed"],
      ["acceleration_0_100_s", "Acceleration 0–100"],
      ["torque_nm", "Torque"],
      ["fast_charging_power_kw_dc", "Fast charging power"],
      ["towing_capacity_kg", "Towing capacity"],
      ["seats", "Seats"],
      ["length_mm", "Length"],
      ["width_mm", "Width"],
      ["height_mm", "Height"],
      ["cargo_volume_l", "Cargo volume"]
    ];

    required.forEach(function ([name, label]) {
      const el = form.elements[name];
      if (!el) return;
      const val = el.value.trim();
      if (val === "") {
        errors.push(label + " is required.");
        el.classList.add("input-error");
      }
    });

    const positives = [
      ["battery_capacity_kWh", "Battery capacity"],
      ["seats", "Seats"],
      ["length_mm", "Length"],
      ["width_mm", "Width"],
      ["height_mm", "Height"],
      ["top_speed_kmh", "Top speed"]
    ];
    positives.forEach(function ([name, label]) {
      const el = form.elements[name];
      if (el && el.value !== "" && parseFloat(el.value) <= 0) {
        errors.push(label + " must be greater than 0.");
        el.classList.add("input-error");
      }
    });

    return errors;
  }

  function buildPayload() {
    const payload = {};
    const numerics = [
      "top_speed_kmh", "battery_capacity_kWh", "torque_nm",
      "acceleration_0_100_s", "fast_charging_power_kw_dc",
      "towing_capacity_kg", "seats", "length_mm", "width_mm",
      "height_mm", "cargo_volume_l"
    ];

    numerics.forEach(function (name) {
      const val = form.elements[name].value.trim();
      payload[name] = val !== "" ? parseFloat(val) : null;
    });

    if (cellsMissing.checked) {
      payload.number_of_cells = null;
      payload.cells_missing_flag = 1;
    } else {
      const ncVal = cellsInput.value.trim();
      payload.number_of_cells = ncVal !== "" ? parseFloat(ncVal) : null;
      payload.cells_missing_flag = (ncVal === "") ? 1 : 0;
    }

    payload.drivetrain = form.elements["drivetrain"].value;
    payload.segment = form.elements["segment"].value;
    payload.car_body_type = form.elements["car_body_type"].value;

    return payload;
  }

  function updateRangeBar(value) {
    const clamped = Math.max(RANGE_MIN, Math.min(RANGE_MAX, value));
    const pct = ((clamped - RANGE_MIN) / (RANGE_MAX - RANGE_MIN)) * 100;
    rangeBarFill.style.width = pct + "%";
    rangeBarMark.style.left = pct + "%";
  }

  function renderReceivedInput(received) {
    if (!received || !inputSummaryG) return;
    inputSummaryG.innerHTML = "";
    const keyMap = {
      battery_capacity_kWh: "Battery",
      car_body_type: "Body",
      drivetrain: "Drivetrain",
      seats: "Seats",
      top_speed_kmh: "Top Speed"
    };
    Object.keys(received).forEach(function (k) {
      if (received[k] === undefined || received[k] === null) return;
      const kEl = document.createElement("span");
      kEl.className = "input-summary-key";
      kEl.textContent = keyMap[k] || k;

      const vEl = document.createElement("span");
      vEl.className = "input-summary-val mono";
      let valStr = received[k];
      if (k === "battery_capacity_kWh") valStr += " kWh";
      if (k === "top_speed_kmh") valStr += " km/h";
      vEl.textContent = valStr;

      inputSummaryG.appendChild(kEl);
      inputSummaryG.appendChild(vEl);
    });
    inputSummary.classList.remove("hidden");
  }

  // Local storage history
  function saveToHistory(item) {
    try {
      let history = JSON.parse(localStorage.getItem("ev_range_history") || "[]");
      history.unshift(item);
      if (history.length > 5) history = history.slice(0, 5);
      localStorage.setItem("ev_range_history", JSON.stringify(history));
      renderHistory();
    } catch (e) {}
  }

  function renderHistory() {
    if (!historyList || !historyPanel) return;
    try {
      const history = JSON.parse(localStorage.getItem("ev_range_history") || "[]");
      if (history.length === 0) {
        historyPanel.classList.add("hidden");
        return;
      }
      historyList.innerHTML = "";
      history.forEach(function (item) {
        const div = document.createElement("div");
        div.className = "history-item";
        div.innerHTML = `<span class="history-item-desc">${item.body} &middot; ${item.battery} kWh</span><span class="history-item-val mono">${Math.round(item.range)} km</span>`;
        historyList.appendChild(div);
      });
      historyPanel.classList.remove("hidden");
    } catch (e) {}
  }

  // Form submit
  form.addEventListener("submit", function (e) {
    e.preventDefault();

    const errors = validateForm();
    if (errors.length > 0) {
      errorMsg.textContent = errors[0];
      showState(stateError);
      return;
    }

    const payload = buildPayload();
    showState(stateLoading);
    btnPredict.disabled = true;

    fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        return res.json().then(function (data) {
          return { status: res.status, body: data };
        });
      })
      .then(function (result) {
        btnPredict.disabled = false;

        if (result.status !== 200) {
          const msg = result.body.errors
            ? result.body.errors.join(" ")
            : result.body.error || "Prediction failed.";
          errorMsg.textContent = msg;
          showState(stateError);
          return;
        }

        const range = result.body.predicted_range_km;
        resultNumber.textContent = Math.round(range);
        updateRangeBar(range);
        renderReceivedInput(result.body.received_input);
        showState(stateSuccess);

        saveToHistory({
          body: payload.car_body_type,
          battery: payload.battery_capacity_kWh,
          range: range
        });
      })
      .catch(function () {
        btnPredict.disabled = false;
        errorMsg.textContent = "Prediction service unavailable. Ensure Flask app is running.";
        showState(stateError);
      });
  });

  // Initial history render
  renderHistory();
})();
