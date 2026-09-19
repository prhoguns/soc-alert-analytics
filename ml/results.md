# Anomaly detection results

Host-hours scored: **13,675** (49 hosts × 30 days). Host-hours containing a planted alert: **10** (0.07%).

Isolation Forest (300 trees, no labels) vs. the baseline of ranking by raw alert count:

| top-k | Isolation Forest P / R | excess-sum heuristic P / R | raw volume baseline P / R | combined P / R |
|---:|---:|---:|---:|---:|
| 10 | 0.00 / 0.00 | 0.20 / 0.20 | 0.20 / 0.20 | 0.20 / 0.20 |
| 25 | 0.00 / 0.00 | 0.08 / 0.20 | 0.08 / 0.20 | 0.08 / 0.20 |
| 50 | 0.04 / 0.20 | 0.04 / 0.20 | 0.04 / 0.20 | 0.06 / 0.30 |
| 100 | 0.03 / 0.30 | 0.02 / 0.20 | 0.02 / 0.20 | 0.04 / 0.40 |

Where each planted incident first appears in the ranking (1 = most anomalous host-hour):

| incident | host-hour | Isolation Forest | excess heuristic | raw volume | combined |
|---|---|---:|---:|---:|---:|
| ssh_brute_force_vpn01 | vpn-01 2026-08-10T03:00 | 193 | 1 | 2 | 2 |
| lateral_movement_ws017_dc01 | ws-017 2026-08-17T14:00 | 46 | 2173 | 5596 | 65 |
| web_scan_sqli_web01 | web-01 2026-08-24T22:00 | 63 | 4 | 1 | 7 |

## Top 15 most anomalous host-hours

| rank | host | hour | alerts | rules | tactics | users | ext IPs | max lvl | score | planted? |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | app-01 | 2026-08-05 14:00 | 19 | 7 | 3 | 19 | 0 | 10 | 0.750 |  |
| 2 | ws-023 | 2026-08-11 02:00 | 8 | 6 | 5 | 8 | 0 | 12 | 0.750 |  |
| 3 | vpn-01 | 2026-08-17 15:00 | 10 | 5 | 2 | 9 | 5 | 10 | 0.723 |  |
| 4 | web-01 | 2026-08-11 11:00 | 50 | 5 | 3 | 36 | 18 | 10 | 0.722 |  |
| 5 | vpn-01 | 2026-08-24 14:00 | 16 | 4 | 1 | 14 | 7 | 10 | 0.720 |  |
| 6 | vpn-01 | 2026-08-19 13:00 | 13 | 4 | 1 | 12 | 7 | 10 | 0.717 |  |
| 7 | vpn-01 | 2026-08-14 16:00 | 13 | 4 | 1 | 13 | 9 | 10 | 0.716 |  |
| 8 | ws-030 | 2026-08-11 02:00 | 5 | 4 | 3 | 5 | 0 | 8 | 0.716 |  |
| 9 | ws-002 | 2026-08-11 02:00 | 6 | 5 | 4 | 6 | 0 | 9 | 0.712 |  |
| 10 | vpn-01 | 2026-08-12 15:00 | 10 | 3 | 2 | 9 | 5 | 7 | 0.711 |  |
| 11 | vpn-01 | 2026-08-25 14:00 | 11 | 4 | 1 | 11 | 5 | 10 | 0.711 |  |
| 12 | web-01 | 2026-08-11 16:00 | 52 | 7 | 2 | 36 | 18 | 10 | 0.710 |  |
| 13 | db-01 | 2026-08-19 10:00 | 18 | 5 | 2 | 17 | 0 | 9 | 0.710 |  |
| 14 | vpn-01 | 2026-08-26 13:00 | 10 | 4 | 1 | 10 | 7 | 10 | 0.707 |  |
| 15 | web-01 | 2026-08-07 15:00 | 56 | 6 | 2 | 36 | 19 | 10 | 0.706 |  |

## What makes a host-hour anomalous here

Features whose values in the top 25 differ most from the population (|z| of the mean):

- `high_sev_alerts_excess`: 4.6
- `external_ips_excess`: 4.1
- `distinct_rules_excess`: 3.5
- `alerts_excess`: 3.5
- `distinct_users_excess`: 3.4
- `tactic_initial_access_excess`: 3.3

See README for the interpretation and the caveats.
