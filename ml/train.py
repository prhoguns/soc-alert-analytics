"""Unsupervised anomaly detection over host-hours, evaluated against the planted incidents.

    python ml/train.py            # trains, scores, writes ml/results.md and charts/ml_anomaly_scores.png

Method: IsolationForest on the feature matrix from ml/features.py. No labels are used for training.
Evaluation: data/planted.json lists the alert ids the generator planted; a host-hour is "malicious"
if it contains at least one planted alert. We report precision/recall at the top-k and compare with
the obvious baseline (rank host-hours by raw alert count), which is what a volume threshold does.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import matplotlib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ml.features import FEATURE_COLUMNS, build, matrix  # noqa: E402

DB = "data/soc.duckdb"
SEED = 42


def malicious_host_hours(db_path: str, planted_ids: list[str]) -> set[tuple[str, pd.Timestamp]]:
    con = duckdb.connect(db_path, read_only=True)
    con.execute("create temp table planted (id varchar)")
    con.executemany("insert into planted values (?)", [(i,) for i in planted_ids])
    rows = con.execute(
        "select distinct agent, date_trunc('hour', ts) from alerts where alert_id in (select id from planted)"
    ).fetchall()
    con.close()
    return {(a, pd.Timestamp(h).tz_convert("UTC").tz_localize(None) if pd.Timestamp(h).tzinfo else pd.Timestamp(h)) for a, h in rows}


def precision_recall_at_k(ranked: pd.DataFrame, truth: set, k: int) -> tuple[float, float]:
    top = ranked.head(k)
    hits = sum((a, h) in truth for a, h in zip(top["agent"], top["hour"], strict=True))
    return hits / k, hits / len(truth)


def main() -> None:
    planted = json.load(open("data/planted.json"))
    df = build(DB)
    X = matrix(df)
    truth = malicious_host_hours(DB, planted["planted_alert_ids"])

    model = IsolationForest(n_estimators=300, contamination="auto", random_state=SEED)
    model.fit(X)
    df["anomaly_score"] = -model.score_samples(X)  # higher = more anomalous
    df["is_malicious"] = [(a, h) in truth for a, h in zip(df["agent"], df["hour"], strict=True)]

    # Transparent comparator: the sum of per-feature excess. If a black-box model cannot beat this, use this.
    df["excess_score"] = X[[c for c in X.columns if c.endswith("_excess")]].sum(axis=1)
    ranked = df.sort_values("anomaly_score", ascending=False).reset_index()
    baseline = df.sort_values("alerts", ascending=False).reset_index()
    heuristic = df.sort_values("excess_score", ascending=False).reset_index()
    # Combined: best rank from either method. Loud attacks come from the heuristic, quiet ones from the forest.
    df["if_rank"] = df["anomaly_score"].rank(ascending=False, method="first")
    df["heur_rank"] = df["excess_score"].rank(ascending=False, method="first")
    df["combined_rank"] = df[["if_rank", "heur_rank"]].min(axis=1)
    combined = df.sort_values(["combined_rank", "anomaly_score"], ascending=[True, False]).reset_index()
    n = len(df)
    ks = [10, 25, 50, 100]

    lines = [
        "# Anomaly detection results", "",
        f"Host-hours scored: **{n:,}** ({df['agent'].nunique()} hosts × 30 days). "
        f"Host-hours containing a planted alert: **{len(truth)}** ({100 * len(truth) / n:.2f}%).", "",
        "Isolation Forest (300 trees, no labels) vs. the baseline of ranking by raw alert count:", "",
        "| top-k | Isolation Forest P / R | excess-sum heuristic P / R | raw volume baseline P / R | combined P / R |",
        "|---:|---:|---:|---:|---:|",
    ]
    for k in ks:
        p, r = precision_recall_at_k(ranked, truth, k)
        hp, hr = precision_recall_at_k(heuristic, truth, k)
        bp, br = precision_recall_at_k(baseline, truth, k)
        cp, cr = precision_recall_at_k(combined, truth, k)
        lines.append(f"| {k} | {p:.2f} / {r:.2f} | {hp:.2f} / {hr:.2f} | {bp:.2f} / {br:.2f} | {cp:.2f} / {cr:.2f} |")

    # Rank of the first host-hour of each planted incident
    lines += ["", "Where each planted incident first appears in the ranking (1 = most anomalous host-hour):", "",
              "| incident | host-hour | Isolation Forest | excess heuristic | raw volume | combined |", "|---|---|---:|---:|---:|---:|"]
    for name, hour in planted["incidents"].items():
        host = {"ssh_brute_force_vpn01": "vpn-01", "lateral_movement_ws017_dc01": "ws-017", "web_scan_sqli_web01": "web-01"}[name]
        ts = pd.Timestamp(hour + ":00:00")
        def rank_in(tbl):
            idx = tbl.index[(tbl["agent"] == host) & (tbl["hour"] == ts)]
            return int(idx[0]) + 1 if len(idx) else "-"

        lines.append(f"| {name} | {host} {hour}:00 | {rank_in(ranked)} | {rank_in(heuristic)} | {rank_in(baseline)} | {rank_in(combined)} |")

    lines += ["", "## Top 15 most anomalous host-hours", "",
              "| rank | host | hour | alerts | rules | tactics | users | ext IPs | max lvl | score | planted? |",
              "|---:|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|"]
    for i, r in ranked.head(15).iterrows():
        lines.append(
            f"| {i + 1} | {r.agent} | {r.hour:%Y-%m-%d %H:00} | {int(r.alerts)} | {int(r.distinct_rules)} | {int(r.distinct_tactics)} | "
            f"{int(r.distinct_users)} | {int(r.external_ips)} | {int(r.max_level)} | {r.anomaly_score:.3f} | {'yes' if r.is_malicious else ''} |"
        )

    # Feature importance proxy: mean |z| of each feature among the top 25 vs population
    top = X.loc[ranked.head(25)["index"]]
    z = ((top.mean() - X.mean()) / X.std().replace(0, np.nan)).abs().sort_values(ascending=False)
    lines += ["", "## What makes a host-hour anomalous here", "",
              "Features whose values in the top 25 differ most from the population (|z| of the mean):", ""]
    lines += [f"- `{f}`: {v:.1f}" for f, v in z.head(6).items()]
    lines += ["", "See README for the interpretation and the caveats."]
    Path("ml/results.md").write_text("\n".join(lines) + "\n")

    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.hist(df.loc[~df.is_malicious, "anomaly_score"], bins=80, color="#c9d6e3", label="benign host-hours")
    ax.hist(df.loc[df.is_malicious, "anomaly_score"], bins=40, color="#b22222", alpha=0.85, label="host-hours with a planted alert")
    ax.set_yscale("log")
    ax.set_xlabel("Isolation Forest anomaly score (higher = more anomalous)")
    ax.set_title("Anomaly score distribution: planted incidents sit in the right tail")
    ax.legend()
    fig.tight_layout()
    Path("charts").mkdir(exist_ok=True)
    fig.savefig("charts/ml_anomaly_scores.png", dpi=130)

    print("\n".join(lines[:12]))
    print(f"\nfeatures: {len(FEATURE_COLUMNS)}; results -> ml/results.md, charts/ml_anomaly_scores.png")


if __name__ == "__main__":
    main()
