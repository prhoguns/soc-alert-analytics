# Anomaly detection results

Host-hours scored: **13,675** (49 hosts × 30 days). Host-hours containing a planted alert: **10** (0.07%).

Isolation Forest (300 trees, no labels) vs. the baseline of ranking by raw alert count:

| top-k | Isolation Forest P / R | excess-sum heuristic P / R | raw volume baseline P / R | combined P / R |
|---:|---:|---:|---:|---:|
| 10 | 0.00 / 0.00 | 0.20 / 0.20 | 0.20 / 0.20 | 0.20 / 0.20 |
| 25 | 0.00 / 0.00 | 0.08 / 0.20 | 0.08 / 0.20 | 0.08 / 0.20 |
| 50 | 0.04 / 0.20 | 0.04 / 0.20 | 0.04 / 0.20 | 0.04 / 0.20 |
| 100 | 0.04 / 0.40 | 0.02 / 0.20 | 0.02 / 0.20 | 0.04 / 0.40 |

Where each planted incident first appears in the ranking (1 = most anomalous host-hour):

| incident | host-hour | Isolation Forest | excess heuristic | raw volume | combined |
|---|---|---:|---:|---:|---:|
| ssh_brute_force_vpn01 | vpn-01 2026-08-10T03:00 | 123 | 1 | 2 | 2 |
| lateral_movement_ws017_dc01 | ws-017 2026-08-17T14:00 | 47 | 2177 | 3606 | 66 |
| web_scan_sqli_web01 | web-01 2026-08-24T22:00 | 57 | 4 | 1 | 7 |

## Top 15 most anomalous host-hours

| rank | host | hour | alerts | rules | tactics | users | ext IPs | max lvl | score | planted? |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|:---:|
| 1 | ws-023 | 2026-08-11 02:00 | 8 | 6 | 5 | 8 | 0 | 12 | 0.751 |  |
| 2 | app-01 | 2026-08-05 14:00 | 19 | 7 | 3 | 19 | 0 | 10 | 0.744 |  |
| 3 | vpn-01 | 2026-08-17 15:00 | 10 | 5 | 2 | 9 | 5 | 10 | 0.733 |  |
| 4 | web-01 | 2026-08-11 11:00 | 50 | 5 | 3 | 36 | 18 | 10 | 0.722 |  |
| 5 | ws-002 | 2026-08-11 02:00 | 6 | 5 | 4 | 6 | 0 | 9 | 0.716 |  |
| 6 | ws-030 | 2026-08-11 02:00 | 5 | 4 | 3 | 5 | 0 | 8 | 0.713 |  |
| 7 | vpn-01 | 2026-08-14 16:00 | 13 | 4 | 1 | 13 | 9 | 10 | 0.712 |  |
| 8 | vpn-01 | 2026-08-24 14:00 | 16 | 4 | 1 | 14 | 7 | 10 | 0.712 |  |
| 9 | vpn-01 | 2026-08-19 13:00 | 13 | 4 | 1 | 12 | 7 | 10 | 0.711 |  |
| 10 | web-01 | 2026-08-11 16:00 | 52 | 7 | 2 | 36 | 18 | 10 | 0.710 |  |
| 11 | web-01 | 2026-08-07 15:00 | 56 | 6 | 2 | 36 | 19 | 10 | 0.709 |  |
| 12 | vpn-01 | 2026-08-25 14:00 | 11 | 4 | 1 | 11 | 5 | 10 | 0.706 |  |
| 13 | db-01 | 2026-08-19 10:00 | 18 | 5 | 2 | 17 | 0 | 9 | 0.705 |  |
| 14 | app-02 | 2026-08-18 11:00 | 9 | 6 | 3 | 8 | 0 | 10 | 0.705 |  |
| 15 | web-01 | 2026-08-24 08:00 | 49 | 6 | 3 | 34 | 18 | 9 | 0.705 |  |

## What makes a host-hour anomalous here

Features whose values in the top 25 differ most from the population (|z| of the mean):

- `high_sev_alerts_excess`: 4.1
- `external_ips_excess`: 3.7
- `alerts_excess`: 3.5
- `distinct_users_excess`: 3.5
- `distinct_rules_excess`: 3.4
- `distinct_src_ips_excess`: 3.4

See README for the interpretation and the caveats.
