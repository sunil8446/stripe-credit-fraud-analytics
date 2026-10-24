const data = window.FRAUD_DATA;

const palette = {
  mint: "#77f2c4",
  green: "#2ecc9a",
  coral: "#ff786c",
  amber: "#f0b95d",
  muted: "#53615e",
  grid: "rgba(169, 202, 193, 0.10)"
};

Chart.defaults.color = "#8e9e9a";
Chart.defaults.font.family = "DM Mono, monospace";
Chart.defaults.font.size = 10;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.boxWidth = 7;

const number = new Intl.NumberFormat("en-US");
const currency = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });
const percent = (value) => `${Number(value || 0).toFixed(2)}%`;
const scorePercent = (value) => `${(Number(value || 0) * 100).toFixed(1)}%`;

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function barOptions(suffix = "") {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { backgroundColor: "#142720", padding: 12 } },
    scales: {
      x: { grid: { display: false }, border: { display: false } },
      y: { beginAtZero: true, grid: { color: palette.grid }, border: { display: false }, ticks: { callback: (value) => `${value}${suffix}` } }
    }
  };
}

function renderSummary() {
  const summary = data.summary;
  const highest = [...data.segments].sort((a, b) => b.fraud_rate_pct - a.fraud_rate_pct)[0];
  setText("fraud-rate", percent(summary.fraud_rate_pct));
  setText("fraud-count", number.format(summary.fraud_count));
  setText("transaction-count", number.format(summary.transaction_count));
  setText("transaction-amount", currency.format(summary.transaction_amount));
  setText("fraud-amount", currency.format(summary.fraud_amount));
  setText("highest-segment", highest.amount_segment);
  setText("highest-segment-rate", `${percent(highest.fraud_rate_pct)} observed rate`);
  setText("data-source", data.source);
  setText("freshness", new Date(data.generated_at).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" }));
}

function renderCharts() {
  new Chart(document.getElementById("daily-chart"), {
    type: "line",
    data: {
      labels: data.daily.map((item) => item.transaction_date),
      datasets: [
        { label: "Transactions", data: data.daily.map((item) => item.transaction_count), borderColor: palette.mint, backgroundColor: "rgba(119,242,196,.1)", fill: true, tension: .35, yAxisID: "y" },
        { label: "Fraud cases", data: data.daily.map((item) => item.fraud_count), borderColor: palette.coral, backgroundColor: palette.coral, tension: .35, yAxisID: "y1" }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: { legend: { position: "top", align: "end" } },
      scales: {
        x: { grid: { display: false }, border: { display: false } },
        y: { beginAtZero: true, grid: { color: palette.grid }, border: { display: false } },
        y1: { beginAtZero: true, position: "right", grid: { display: false }, border: { display: false } }
      }
    }
  });

  new Chart(document.getElementById("segment-chart"), {
    type: "bar",
    data: { labels: data.segments.map((item) => item.amount_segment), datasets: [{ data: data.segments.map((item) => item.fraud_rate_pct), backgroundColor: [palette.muted, palette.green, palette.mint, palette.amber, palette.coral], borderRadius: 5 }] },
    options: barOptions("%")
  });

  new Chart(document.getElementById("time-chart"), {
    type: "polarArea",
    data: { labels: data.time_of_day.map((item) => item.time_of_day), datasets: [{ data: data.time_of_day.map((item) => item.fraud_rate_pct), backgroundColor: ["rgba(119,242,196,.75)", "rgba(46,204,154,.65)", "rgba(240,185,93,.75)", "rgba(255,120,108,.7)"], borderWidth: 0 }] },
    options: { responsive: true, maintainAspectRatio: false, scales: { r: { beginAtZero: true, grid: { color: palette.grid }, ticks: { display: false }, pointLabels: { display: false } } }, plugins: { legend: { position: "right" } } }
  });

  new Chart(document.getElementById("risk-chart"), {
    type: "doughnut",
    data: { labels: data.risk_tiers.map((item) => item.heuristic_risk_tier), datasets: [{ data: data.risk_tiers.map((item) => item.transaction_count), backgroundColor: [palette.muted, palette.mint, palette.amber, palette.coral], borderWidth: 0, hoverOffset: 3 }] },
    options: { responsive: true, maintainAspectRatio: false, cutout: "72%", plugins: { legend: { display: false } } }
  });
}

function renderRiskTable() {
  const colors = [palette.muted, palette.mint, palette.amber, palette.coral];
  document.getElementById("risk-table").innerHTML = data.risk_tiers.map((item, index) => `
    <div class="risk-row">
      <div class="risk-name"><span class="risk-dot" style="background:${colors[index]}"></span>${item.heuristic_risk_tier}</div>
      <div class="risk-value">${number.format(item.transaction_count)} txns</div>
      <div class="risk-value">${percent(item.observed_fraud_rate_pct)} fraud</div>
    </div>
  `).join("");
}

function renderModel() {
  const model = data.model;
  const metrics = model.performance;
  const isDemo = Number(metrics.sample_count) < 1000;
  setText("average-precision", scorePercent(metrics.average_precision));
  setText("roc-auc", scorePercent(metrics.roc_auc));
  setText("model-recall", scorePercent(metrics.recall));
  setText("false-positive-rate", scorePercent(metrics.false_positive_rate));
  setText("brier-score", Number(metrics.brier_score).toFixed(3));
  setText("cost-savings", percent(metrics.cost_savings_pct));
  setText("true-negative", number.format(metrics.true_negative_count));
  setText("false-positive", number.format(metrics.false_positive_count));
  setText("false-negative", number.format(metrics.false_negative_count));
  setText("true-positive", number.format(metrics.true_positive_count));
  setText("holdout-size", `${number.format(metrics.validation_count)} rows`);
  setText("decision-threshold", scorePercent(metrics.decision_threshold));
  setText("alert-rate", scorePercent(metrics.alert_rate));
  setText("cost-ratio", `${Number(metrics.false_negative_cost).toFixed(0)} : ${Number(metrics.false_positive_cost).toFixed(0)}`);
  setText("model-scope", isDemo ? `Illustrative · ${number.format(metrics.validation_count)}-row temporal holdout` : `Validated · ${number.format(metrics.validation_count)}-row holdout`);
  setText("model-version", `${metrics.model_version} · ${metrics.validation_strategy}`);

  new Chart(document.getElementById("calibration-chart"), {
    type: "scatter",
    data: {
      datasets: [
        { label: "Observed", data: model.calibration.map((item) => ({ x: Number(item.mean_predicted_score), y: Number(item.observed_fraud_rate) })), borderColor: palette.mint, backgroundColor: palette.mint, showLine: true, tension: .2, pointRadius: 4 },
        { label: "Perfect", data: [{ x: 0, y: 0 }, { x: 1, y: 1 }], borderColor: palette.muted, borderDash: [4, 4], showLine: true, pointRadius: 0 }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { position: "top", align: "end" } },
      scales: {
        x: { min: 0, max: 1, title: { display: true, text: "Predicted score" }, grid: { color: palette.grid }, ticks: { callback: (value) => `${value * 100}%` } },
        y: { min: 0, max: 1, title: { display: true, text: "Observed fraud" }, grid: { color: palette.grid }, ticks: { callback: (value) => `${value * 100}%` } }
      }
    }
  });

  document.getElementById("comparison-table").innerHTML = model.comparison.map((item) => `
    <tr>
      <td>${item.model_name}</td>
      <td>${scorePercent(item.average_precision)}</td>
      <td>${scorePercent(item.roc_auc)}</td>
      <td>${scorePercent(item.precision)}</td>
      <td>${scorePercent(item.recall)}</td>
      <td>${Number(item.expected_cost).toFixed(0)} units</td>
      <td><span class="${item.selected_model ? "active-badge" : ""}">${item.selected_model ? "Active" : "Candidate"}</span></td>
    </tr>
  `).join("");

  const bandColors = { low: palette.muted, review: palette.mint, high: palette.amber, critical: palette.coral };
  new Chart(document.getElementById("model-risk-chart"), {
    type: "bar",
    data: {
      labels: model.risk_bands.map((item) => item.risk_band),
      datasets: [{ data: model.risk_bands.map((item) => item.transaction_count), backgroundColor: model.risk_bands.map((item) => bandColors[item.risk_band]), borderRadius: 5 }]
    },
    options: barOptions("")
  });

  new Chart(document.getElementById("outcome-score-chart"), {
    type: "bar",
    data: {
      labels: model.score_by_outcome.map((item) => item.outcome),
      datasets: [
        { label: "Hybrid score", data: model.score_by_outcome.map((item) => Number(item.average_risk_score) * 100), backgroundColor: palette.mint, borderRadius: 4 },
        { label: "Anomaly score", data: model.score_by_outcome.map((item) => Number(item.average_anomaly_score) * 100), backgroundColor: palette.amber, borderRadius: 4 }
      ]
    },
    options: { ...barOptions("%"), plugins: { legend: { display: true, position: "top", align: "end" } } }
  });

  document.getElementById("alert-table").innerHTML = model.top_alerts.map((item) => `
    <tr>
      <td>${item.transaction_id.slice(0, 13)}…</td>
      <td>${currency.format(item.amount)}</td>
      <td><span class="risk-badge">${item.risk_band} · ${scorePercent(item.risk_score)}</span></td>
      <td class="${Number(item.is_fraud) === 1 ? "outcome-fraud" : ""}">${Number(item.is_fraud) === 1 ? "Fraud" : "Legitimate"}</td>
      <td>${item.reason_1}</td>
    </tr>
  `).join("");
}

if (!data) {
  document.body.innerHTML = "<p>Dashboard data is unavailable. Run <code>make demo</code>.</p>";
} else {
  renderSummary();
  renderCharts();
  renderRiskTable();
  renderModel();
}

