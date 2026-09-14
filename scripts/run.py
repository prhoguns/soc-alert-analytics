"""Run every query in sql/ against data/soc.duckdb, write results/<name>.md, and draw the charts.

    python scripts/run.py            # everything
    python scripts/run.py 08 16      # just queries 08 and 16
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import duckdb
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

DB = "data/soc.duckdb"
SQL_DIR = Path("sql")
OUT_DIR = Path("results")
CHART_DIR = Path("charts")
MAX_ROWS = 60


NO_SEPARATOR = ("year", "id", "hour", "rank", "num", "month", "rows", "rn")


def fmt_cell(v, col: str = "") -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)) or v is pd.NaT or v is pd.NA:
        return ""
    sep = "" if any(k in col for k in NO_SEPARATOR) else ","
    if isinstance(v, (bool, np.bool_)):
        return str(v)
    if isinstance(v, (int, np.integer)):
        return f"{int(v):{sep}}"
    if isinstance(v, (float, np.floating)):
        return f"{int(v):{sep}}" if float(v).is_integer() else f"{v:{sep}.1f}"
    if isinstance(v, (pd.Timestamp,)):
        return v.strftime("%Y-%m-%d") if v == v.normalize() else v.strftime("%Y-%m-%d %H:%M")
    return str(v)


def to_markdown(df: pd.DataFrame) -> str:
    """Own renderer: pandas.to_markdown upcasts every column to float when any column is float."""
    cols = list(df.columns)
    numeric = [pd.api.types.is_numeric_dtype(df[c]) for c in cols]
    head = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join("---:" if n else ":---" for n in numeric) + "|"
    rows = ["| " + " | ".join(fmt_cell(v, c) for v, c in zip(rec, cols, strict=True)) + " |" for rec in df.itertuples(index=False, name=None)]
    return "\n".join([head, sep, *rows])


def run_query(con: duckdb.DuckDBPyConnection, path: Path) -> None:
    sql = path.read_text()
    df = con.execute(sql).df()
    question = next((line.lstrip("- ").strip() for line in sql.splitlines() if line.startswith("-- Q")), path.stem)
    body = to_markdown(df.head(MAX_ROWS))
    note = f"\n\n_{len(df):,} rows; showing first {MAX_ROWS}._" if len(df) > MAX_ROWS else f"\n\n_{len(df):,} rows._"
    (OUT_DIR / f"{path.stem}.md").write_text(f"# {question}\n\n```sql\n{sql.strip()}\n```\n\n{body}{note}\n")
    print(f"{path.stem}: {len(df):,} rows")


def charts(con: duckdb.DuckDBPyConnection) -> None:
    CHART_DIR.mkdir(exist_ok=True)
    plt.rcParams.update({"figure.dpi": 130, "axes.spines.top": False, "axes.spines.right": False})

    df = con.execute((SQL_DIR / "01_daily_volume_by_severity.sql").read_text()).df()
    ax = df.set_index("day")[["low", "medium", "high", "critical"]].plot.bar(
        stacked=True, figsize=(10, 4), width=0.85, color=["#c9d6e3", "#7fa6c9", "#1f4e79", "#b22222"]
    )
    ax.set_title("Daily alert volume by severity (Tuesday patch windows visible)")
    ax.set_xticks(range(0, len(df), 3), [d.strftime("%b %d") for d in df["day"][::3]], rotation=0)
    ax.set_xlabel("")
    ax.figure.tight_layout()
    ax.figure.savefig(CHART_DIR / "01_daily_volume.png")

    df = con.execute((SQL_DIR / "02_noisy_rules.sql").read_text()).df().head(12)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = ["#b22222" if r.startswith("TUNE") else "#1f4e79" if r.startswith("KEEP") else "#7fa6c9" for r in df["recommendation"]]
    ax.barh(df["rule_description"].str.slice(0, 48)[::-1], df["alerts"][::-1], color=colors[::-1])
    ax.set_xlabel("alerts in 30 days   (red = tune, blue = keep, light = review)")
    ax.set_title("Top 12 rules by volume with tuning recommendation")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "02_noisy_rules.png")

    df = con.execute((SQL_DIR / "06_hourly_heatmap.sql").read_text()).df()
    grid = df.pivot(index="dow_num", columns="hour", values="alerts")
    fig, ax = plt.subplots(figsize=(10, 3.6))
    im = ax.imshow(grid, aspect="auto", cmap="YlOrRd")
    ax.set_yticks(range(7), ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    ax.set_xticks(range(0, 24, 2), range(0, 24, 2))
    ax.set_xlabel("hour (UTC)")
    ax.set_title("Alerts by weekday and hour")
    fig.colorbar(im, ax=ax, label="alerts")
    fig.tight_layout()
    fig.savefig(CHART_DIR / "06_heatmap.png")

    df = con.execute((SQL_DIR / "04_night_vs_day_triage.sql").read_text()).df()
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(df["hour_fired"], df["mean_min_to_triage"], marker="o", color="#1f4e79", label="mean")
    ax.plot(df["hour_fired"], df["p90_min_to_triage"], marker="o", color="#b22222", label="p90")
    ax.set_xlabel("hour alert fired (UTC)")
    ax.set_ylabel("minutes to triage")
    ax.set_title("Time-to-triage by hour of day, level >= 7")
    ax.legend()
    fig.tight_layout()
    fig.savefig(CHART_DIR / "04_triage_by_hour.png")
    print("charts written")


def main(argv: list[str]) -> None:
    OUT_DIR.mkdir(exist_ok=True)
    con = duckdb.connect(DB, read_only=True)
    files = sorted(SQL_DIR.glob("*.sql"))
    if argv:
        files = [f for f in files if f.name[:2] in argv]
    for f in files:
        run_query(con, f)
    if not argv:
        charts(con)


if __name__ == "__main__":
    main(sys.argv[1:])
