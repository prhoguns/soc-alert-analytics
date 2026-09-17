"""Turn the alert stream into one feature vector per (host, hour).

The unit of analysis is a host-hour because that is what an analyst looks at: "what was ws-017
doing at 14:00". Features describe *breadth* of behaviour (distinct rules, tactics, users, external
IPs) as much as volume, so a host that fires one noisy rule 400 times and a host that fires eight
different rules once each look different.
"""
from __future__ import annotations

import duckdb
import pandas as pd

TACTICS = [
    "Credential Access", "Initial Access", "Persistence", "Privilege Escalation",
    "Execution", "Discovery", "Command and Control", "Impact",
]

FEATURE_SQL = """
with base as (
    select
        agent,
        date_trunc('hour', ts) as hour,
        count(*)                                        as alerts,
        count(distinct rule_id)                         as distinct_rules,
        count(distinct src_user)                        as distinct_users,
        count(distinct src_ip)                          as distinct_src_ips,
        count(distinct src_ip) filter (where src_ip is not null and not src_ip like '10.%') as external_ips,
        max(level)                                      as max_level,
        avg(level)                                      as avg_level,
        count(*) filter (where level >= 10)             as high_sev_alerts,
        count(distinct mitre_tactic)                    as distinct_tactics,
        {tactic_cols}
    from alerts
    group by 1, 2
)
select *,
       extract(hour from hour)::int   as hour_of_day,
       isodow(hour)                   as weekday
from base
"""

COUNT_FEATURES = [
    "alerts", "distinct_rules", "distinct_users", "distinct_src_ips", "external_ips", "high_sev_alerts", "distinct_tactics",
] + [f"tactic_{t.lower().replace(' ', '_')}" for t in TACTICS]


def build(db_path: str = "data/soc.duckdb") -> pd.DataFrame:
    tactic_cols = ",\n        ".join(
        f"count(*) filter (where mitre_tactic = '{t}') as tactic_{t.lower().replace(' ', '_')}" for t in TACTICS
    )
    con = duckdb.connect(db_path, read_only=True)
    df = con.execute(FEATURE_SQL.format(tactic_cols=tactic_cols)).df()
    con.close()
    df["hour"] = pd.to_datetime(df["hour"], utc=True).dt.tz_localize(None)
    # Known maintenance window (Tuesday 02:00-04:00 UTC patching). Baselines are computed separately for it,
    # so the weekly FIM storm is "normal for a patch window" instead of the most anomalous thing in the data.
    df["maintenance_window"] = ((df["weekday"] == 2) & (df["hour_of_day"].between(2, 3))).astype(int)
    return df


FEATURE_COLUMNS = [f"{c}_excess" for c in COUNT_FEATURES] + ["max_level", "avg_level"]


def matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Per-host robust z-scores, positive part only.

    Raw counts make Isolation Forest flag *quiet* hours on busy hosts (one alert on web-01 is rare).
    Scoring each host against its own median and MAD, and keeping only the excess above baseline,
    encodes what an analyst means by anomalous: this host is doing *more* / *different* than it usually does.
    """
    import numpy as np

    out = df[["agent"]].copy()
    for c in COUNT_FEATURES:
        g = df.groupby(["agent", "maintenance_window"])[c]
        med = g.transform("median")
        mad = g.transform(lambda s: (s - s.median()).abs().median()).replace(0, 1.0)
        out[f"{c}_excess"] = np.log1p(((df[c] - med) / mad).clip(lower=0))
    out["max_level"] = df["max_level"]
    out["avg_level"] = df["avg_level"]
    return out[FEATURE_COLUMNS]
