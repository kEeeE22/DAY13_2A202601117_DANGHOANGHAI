from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from string import Template
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = REPO_ROOT / "data" / "logs.jsonl"
CONFIG_PATH = REPO_ROOT / "config" / "dashboard.yaml"
EVIDENCE_DIR = REPO_ROOT / "submission" / "evidence"
HTML_PATH = EVIDENCE_DIR / "dashboard.html"
SUMMARY_PATH = EVIDENCE_DIR / "dashboard-summary.json"


def percentile(values: list[float], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])


def load_records(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    if not path.exists():
        return records
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        records.append(json.loads(line))
    return records


def minute_bucket(ts: str | None) -> str:
    if not ts:
        return "unknown"
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return "unknown"
    return parsed.astimezone(timezone.utc).strftime("%H:%M")


def build_summary(records: list[dict[str, Any]]) -> dict[str, Any]:
    requests = [row for row in records if row.get("event") == "request_received"]
    responses = [row for row in records if row.get("event") == "response_sent"]
    failures = [row for row in records if row.get("event") == "request_failed"]
    latency_values = [float(row.get("latency_ms") or 0) for row in responses]
    cost_values = [float(row.get("cost_usd") or 0) for row in responses]
    quality_values = [float(row.get("quality_score") or 0) for row in responses]
    total_requests = len(requests)
    total_errors = len(failures)

    traffic_by_minute = Counter(minute_bucket(row.get("ts")) for row in requests)
    cost_by_minute: defaultdict[str, float] = defaultdict(float)
    for row in responses:
        cost_by_minute[minute_bucket(row.get("ts"))] += float(row.get("cost_usd") or 0)

    return {
        "latency": {
            "p50_ms": round(percentile(latency_values, 50), 2),
            "p95_ms": round(percentile(latency_values, 95), 2),
            "p99_ms": round(percentile(latency_values, 99), 2),
        },
        "traffic": {
            "request_count": total_requests,
            "requests_per_minute": dict(sorted(traffic_by_minute.items())),
        },
        "errors": {
            "error_rate_pct": round((total_errors / total_requests * 100) if total_requests else 0.0, 2),
            "breakdown": dict(Counter(row.get("error_type", "unknown") for row in failures)),
        },
        "cost": {
            "total_usd": round(sum(cost_values), 6),
            "avg_usd": round(mean(cost_values), 6) if cost_values else 0.0,
            "cost_by_minute": {key: round(value, 6) for key, value in sorted(cost_by_minute.items())},
        },
        "tokens": {
            "tokens_in_total": sum(int(row.get("tokens_in") or 0) for row in responses),
            "tokens_out_total": sum(int(row.get("tokens_out") or 0) for row in responses),
        },
        "quality": {
            "quality_avg": round(mean(quality_values), 4) if quality_values else 0.0,
        },
    }


def threshold_for(panel_id: str, config: dict[str, Any]) -> dict[str, Any]:
    for panel in config["dashboard"]["panels"]:
        if panel["id"] == panel_id:
            return panel["threshold"]
    return {}


def render_html(summary: dict[str, Any], config: dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    dashboard = config["dashboard"]
    template = Template(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>$title</title>
  <style>
    :root { color-scheme: light; font-family: Inter, Segoe UI, Arial, sans-serif; }
    body { margin: 0; background: #f5f7fb; color: #18202f; }
    main { max-width: 1180px; margin: 0 auto; padding: 28px; }
    header { display: flex; justify-content: space-between; gap: 16px; align-items: end; margin-bottom: 20px; }
    h1 { margin: 0; font-size: 28px; }
    .meta { color: #5d6678; font-size: 14px; text-align: right; }
    .grid { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 14px; }
    .panel { background: white; border: 1px solid #d9deea; border-radius: 8px; padding: 16px; min-height: 154px; }
    .panel h2 { margin: 0 0 12px; font-size: 16px; }
    .value { font-size: 30px; font-weight: 750; margin: 8px 0; }
    .subgrid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
    .metric { background: #eef2f8; border-radius: 6px; padding: 10px; }
    .label { color: #5d6678; font-size: 12px; }
    .small { font-size: 13px; color: #3e485a; line-height: 1.5; }
    .ok { color: #166534; }
    .warn { color: #b45309; }
    pre { margin: 0; white-space: pre-wrap; font-size: 12px; }
    @media (max-width: 860px) { .grid { grid-template-columns: 1fr; } header { display: block; } .meta { text-align: left; margin-top: 8px; } }
  </style>
</head>
<body>
<main>
  <header>
    <div>
      <h1>$title</h1>
      <div class="small">Source: data/logs.jsonl</div>
    </div>
    <div class="meta">Time range: $time_range minutes<br>Refresh: $refresh seconds<br>Generated: $generated_at</div>
  </header>
  <section class="grid">
    <article class="panel">
      <h2>Latency percentiles</h2>
      <div class="subgrid">
        <div class="metric"><div class="label">P50</div><div class="value">$latency_p50</div><div class="label">ms</div></div>
        <div class="metric"><div class="label">P95</div><div class="value">$latency_p95</div><div class="label">ms</div></div>
        <div class="metric"><div class="label">P99</div><div class="value">$latency_p99</div><div class="label">ms</div></div>
      </div>
      <p class="small">SLO: p95 $latency_operator $latency_threshold ms</p>
    </article>
    <article class="panel">
      <h2>Request traffic</h2>
      <div class="value">$request_count</div>
      <p class="small">Unit: requests per minute. SLO: rate $traffic_operator $traffic_threshold.</p>
      <pre>$traffic_series</pre>
    </article>
    <article class="panel">
      <h2>Error rate and breakdown</h2>
      <div class="value $error_class">$error_rate%</div>
      <p class="small">SLO: error_rate_pct $error_operator $error_threshold%.</p>
      <pre>$error_breakdown</pre>
    </article>
    <article class="panel">
      <h2>Cost over time</h2>
      <div class="value">$total_cost</div>
      <p class="small">USD total. SLO: total $cost_operator $cost_threshold USD.</p>
      <pre>$cost_series</pre>
    </article>
    <article class="panel">
      <h2>Input and output tokens</h2>
      <div class="subgrid">
        <div class="metric"><div class="label">Input</div><div class="value">$tokens_in</div></div>
        <div class="metric"><div class="label">Output</div><div class="value">$tokens_out</div></div>
        <div class="metric"><div class="label">Total</div><div class="value">$tokens_total</div></div>
      </div>
      <p class="small">SLO: sum_by_field $tokens_operator $tokens_threshold tokens.</p>
    </article>
    <article class="panel">
      <h2>Quality proxy</h2>
      <div class="value $quality_class">$quality_avg</div>
      <p class="small">Unit: score 0 to 1. SLO: mean $quality_operator $quality_threshold.</p>
    </article>
  </section>
</main>
</body>
</html>
"""
    )

    latency_threshold = threshold_for("latency", config)
    traffic_threshold = threshold_for("traffic", config)
    error_threshold = threshold_for("errors", config)
    cost_threshold = threshold_for("cost", config)
    tokens_threshold = threshold_for("tokens", config)
    quality_threshold = threshold_for("quality", config)
    error_rate = summary["errors"]["error_rate_pct"]
    quality_avg = summary["quality"]["quality_avg"]

    return template.substitute(
        title=dashboard["title"],
        time_range=dashboard["time_range_minutes"],
        refresh=dashboard["refresh_seconds"],
        generated_at=generated_at,
        latency_p50=summary["latency"]["p50_ms"],
        latency_p95=summary["latency"]["p95_ms"],
        latency_p99=summary["latency"]["p99_ms"],
        latency_operator=latency_threshold["operator"],
        latency_threshold=latency_threshold["value"],
        request_count=summary["traffic"]["request_count"],
        traffic_operator=traffic_threshold["operator"],
        traffic_threshold=traffic_threshold["value"],
        traffic_series=json.dumps(summary["traffic"]["requests_per_minute"], indent=2),
        error_rate=error_rate,
        error_class="ok" if error_rate <= error_threshold["value"] else "warn",
        error_operator=error_threshold["operator"],
        error_threshold=error_threshold["value"],
        error_breakdown=json.dumps(summary["errors"]["breakdown"], indent=2),
        total_cost=f"${summary['cost']['total_usd']}",
        cost_operator=cost_threshold["operator"],
        cost_threshold=cost_threshold["value"],
        cost_series=json.dumps(summary["cost"]["cost_by_minute"], indent=2),
        tokens_in=summary["tokens"]["tokens_in_total"],
        tokens_out=summary["tokens"]["tokens_out_total"],
        tokens_total=summary["tokens"]["tokens_in_total"] + summary["tokens"]["tokens_out_total"],
        tokens_operator=tokens_threshold["operator"],
        tokens_threshold=tokens_threshold["value"],
        quality_avg=quality_avg,
        quality_class="ok" if quality_avg >= quality_threshold["value"] else "warn",
        quality_operator=quality_threshold["operator"],
        quality_threshold=quality_threshold["value"],
    )


def main() -> int:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    records = load_records(LOG_PATH)
    config = yaml.safe_load(CONFIG_PATH.read_text(encoding="utf-8"))
    summary = build_summary(records)
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    HTML_PATH.write_text(render_html(summary, config), encoding="utf-8")
    print(f"Wrote {HTML_PATH.relative_to(REPO_ROOT)}")
    print(f"Wrote {SUMMARY_PATH.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
