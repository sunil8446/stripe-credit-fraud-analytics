#!/usr/bin/env python3
"""Build a pre-rendered dashboard for repository-hosted HTML previews."""

# ruff: noqa: E501 - Generated HTML and CSS fragments are clearer unwrapped.

from __future__ import annotations

import json
import re
from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DASHBOARD = ROOT / "dashboard"

SNAPSHOT_STYLES = """
.snapshot-list { display: grid; gap: 12px; height: 100%; align-content: center; }
.snapshot-row { display: grid; grid-template-columns: minmax(76px, 1fr) 3fr auto; gap: 12px; align-items: center; }
.snapshot-row > span:first-child { color: var(--muted); text-transform: capitalize; font: 500 11px/1.2 "DM Mono", monospace; }
.snapshot-row strong { color: var(--text); font: 600 12px/1.2 "DM Mono", monospace; white-space: nowrap; }
.snapshot-track { height: 7px; overflow: hidden; border-radius: 999px; background: rgba(169, 202, 193, .1); }
.snapshot-fill { height: 100%; min-width: 2px; border-radius: inherit; background: linear-gradient(90deg, var(--mint), var(--green)); }
"""


def load_data() -> dict[str, Any]:
    source = (DASHBOARD / "data" / "dashboard-data.js").read_text(encoding="utf-8")
    prefix = "window.FRAUD_DATA = "
    if not source.startswith(prefix) or not source.rstrip().endswith(";"):
        raise ValueError("Unexpected dashboard data format")
    return json.loads(source[len(prefix) :].rstrip()[:-1])


def replace_text(document: str, element_id: str, value: object) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[a-z]+)[^>]*\bid="{re.escape(element_id)}"[^>]*>).*?(</(?P=tag)>)',
        re.DOTALL,
    )
    updated, count = pattern.subn(rf"\g<1>{escape(str(value))}\g<3>", document, count=1)
    if count != 1:
        raise ValueError(f"Dashboard element not found: {element_id}")
    return updated


def replace_inner(document: str, element_id: str, content: str) -> str:
    pattern = re.compile(
        rf'(<(?P<tag>[a-z]+)[^>]*\bid="{re.escape(element_id)}"[^>]*>).*?(</(?P=tag)>)',
        re.DOTALL,
    )
    updated, count = pattern.subn(rf"\g<1>{content}\g<3>", document, count=1)
    if count != 1:
        raise ValueError(f"Dashboard element not found: {element_id}")
    return updated


def number(value: object) -> str:
    return f"{int(value):,}"


def currency(value: object) -> str:
    return f"${float(value):,.0f}"


def percent(value: object) -> str:
    return f"{float(value):.2f}%"


def score_percent(value: object) -> str:
    return f"{float(value) * 100:.1f}%"


def snapshot_rows(rows: list[tuple[str, float, str]], maximum: float | None = None) -> str:
    ceiling = maximum or max((value for _, value, _ in rows), default=1) or 1
    return '<div class="snapshot-list">' + "".join(
        '<div class="snapshot-row">'
        f"<span>{escape(label)}</span>"
        f'<div class="snapshot-track"><div class="snapshot-fill" style="width:{max(2, min(100, value / ceiling * 100)):.1f}%"></div></div>'
        f"<strong>{escape(display)}</strong>"
        "</div>"
        for label, value, display in rows
    ) + "</div>"


def render_summary(document: str, data: dict[str, Any]) -> str:
    summary = data["summary"]
    highest = max(data["segments"], key=lambda item: item["fraud_rate_pct"])
    generated = datetime.fromisoformat(data["generated_at"]).strftime("%b %d, %Y · %H:%M UTC")
    values = {
        "fraud-rate": percent(summary["fraud_rate_pct"]),
        "fraud-count": number(summary["fraud_count"]),
        "transaction-count": number(summary["transaction_count"]),
        "transaction-amount": currency(summary["transaction_amount"]),
        "fraud-amount": currency(summary["fraud_amount"]),
        "highest-segment": highest["amount_segment"],
        "highest-segment-rate": f'{percent(highest["fraud_rate_pct"])} observed rate',
        "data-source": data["source"],
        "freshness": generated,
    }
    for element_id, value in values.items():
        document = replace_text(document, element_id, value)
    return document


def render_model(document: str, data: dict[str, Any]) -> str:
    model = data["model"]
    metrics = model["performance"]
    values = {
        "average-precision": score_percent(metrics["average_precision"]),
        "roc-auc": score_percent(metrics["roc_auc"]),
        "model-recall": score_percent(metrics["recall"]),
        "false-positive-rate": score_percent(metrics["false_positive_rate"]),
        "brier-score": f'{float(metrics["brier_score"]):.3f}',
        "cost-savings": percent(metrics["cost_savings_pct"]),
        "true-negative": number(metrics["true_negative_count"]),
        "false-positive": number(metrics["false_positive_count"]),
        "false-negative": number(metrics["false_negative_count"]),
        "true-positive": number(metrics["true_positive_count"]),
        "holdout-size": f'{number(metrics["validation_count"])} rows',
        "decision-threshold": score_percent(metrics["decision_threshold"]),
        "alert-rate": score_percent(metrics["alert_rate"]),
        "cost-ratio": f'{float(metrics["false_negative_cost"]):.0f} : {float(metrics["false_positive_cost"]):.0f}',
        "model-scope": f'Illustrative · {number(metrics["validation_count"])}-row temporal holdout',
        "model-version": f'{metrics["model_version"]} · {metrics["validation_strategy"]}',
    }
    for element_id, value in values.items():
        document = replace_text(document, element_id, value)

    comparison = "".join(
        "<tr>"
        f'<td>{escape(item["model_name"])}</td>'
        f'<td>{score_percent(item["average_precision"])}</td>'
        f'<td>{score_percent(item["roc_auc"])}</td>'
        f'<td>{score_percent(item["precision"])}</td>'
        f'<td>{score_percent(item["recall"])}</td>'
        f'<td>{float(item["expected_cost"]):.0f} units</td>'
        f'<td><span class="{"active-badge" if item["selected_model"] else ""}">{"Active" if item["selected_model"] else "Candidate"}</span></td>'
        "</tr>"
        for item in model["comparison"]
    )
    document = replace_inner(document, "comparison-table", comparison)

    alerts = "".join(
        "<tr>"
        f'<td>{escape(item["transaction_id"])}</td>'
        f'<td>{currency(item["amount"])}</td>'
        f'<td><span class="risk-badge">{escape(item["risk_band"])} · {score_percent(item["risk_score"])}</span></td>'
        f'<td class="{"outcome-fraud" if int(item["is_fraud"]) == 1 else ""}">{"Fraud" if int(item["is_fraud"]) == 1 else "Legitimate"}</td>'
        f'<td>{escape(item["reason_1"])}</td>'
        "</tr>"
        for item in model["top_alerts"]
    )
    return replace_inner(document, "alert-table", alerts)


def render_static_charts(document: str, data: dict[str, Any]) -> str:
    risk_table = "".join(
        '<div class="risk-row">'
        f'<div class="risk-name">{escape(item["heuristic_risk_tier"])}</div>'
        f'<div class="risk-value">{number(item["transaction_count"])} txns</div>'
        f'<div class="risk-value">{percent(item["observed_fraud_rate_pct"])} fraud</div>'
        "</div>"
        for item in data["risk_tiers"]
    )
    document = replace_inner(document, "risk-table", risk_table)

    charts = {
        "daily-chart": snapshot_rows([
            (item["transaction_date"], float(item["transaction_count"]), f'{number(item["transaction_count"])} tx · {number(item["fraud_count"])} fraud')
            for item in data["daily"]
        ]),
        "segment-chart": snapshot_rows([
            (item["amount_segment"], float(item["fraud_rate_pct"]), percent(item["fraud_rate_pct"]))
            for item in data["segments"]
        ], 100),
        "time-chart": snapshot_rows([
            (item["time_of_day"], float(item["fraud_rate_pct"]), percent(item["fraud_rate_pct"]))
            for item in data["time_of_day"]
        ], 100),
        "risk-chart": snapshot_rows([
            (item["heuristic_risk_tier"], float(item["transaction_count"]), f'{number(item["transaction_count"])} tx')
            for item in data["risk_tiers"]
        ]),
        "calibration-chart": snapshot_rows([
            (f'bin {item["bin"]}', float(item["observed_fraud_rate"]), f'{score_percent(item["mean_predicted_score"])} predicted · {score_percent(item["observed_fraud_rate"])} observed')
            for item in data["model"]["calibration"]
        ], 1),
        "model-risk-chart": snapshot_rows([
            (item["risk_band"], float(item["transaction_count"]), f'{number(item["transaction_count"])} tx')
            for item in data["model"]["risk_bands"]
        ]),
        "outcome-score-chart": snapshot_rows([
            (item["outcome"], float(item["average_risk_score"]), f'{score_percent(item["average_risk_score"])} hybrid · {score_percent(item["average_anomaly_score"])} anomaly')
            for item in data["model"]["score_by_outcome"]
        ], 1),
    }
    for canvas_id, content in charts.items():
        pattern = re.compile(rf'<canvas\s+id="{re.escape(canvas_id)}"\s*></canvas>')
        document, count = pattern.subn(content, document, count=1)
        if count != 1:
            raise ValueError(f"Dashboard canvas not found: {canvas_id}")
    return document


def main() -> None:
    data = load_data()
    document = (DASHBOARD / "index.html").read_text(encoding="utf-8")
    styles = (DASHBOARD / "styles.css").read_text(encoding="utf-8") + SNAPSHOT_STYLES
    document = document.replace(
        '<link rel="stylesheet" href="styles.css" />', f"<style>\n{styles}\n</style>", 1
    )
    document = re.sub(r'\s*<script[^>]+chart\.umd\.min\.js"></script>', "", document, count=1)
    document = render_summary(document, data)
    document = render_model(document, data)
    document = render_static_charts(document, data)
    document = document.replace('    <script src="data/dashboard-data.js"></script>\n', "")
    document = document.replace('    <script src="app.js"></script>\n', "")

    output = DASHBOARD / "standalone.html"
    output.write_text(document, encoding="utf-8")
    print(f"Built pre-rendered dashboard at {output}")


if __name__ == "__main__":
    main()
