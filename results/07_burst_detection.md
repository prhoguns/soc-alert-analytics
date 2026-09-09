# Q7. Alert bursts: hours where a (rule, agent) pair fired > 5 standard deviations above its own hourly mean.

```sql
-- Q7. Alert bursts: hours where a (rule, agent) pair fired > 5 standard deviations above its own hourly mean.
-- This finds the planted brute force and web scan without knowing they exist.
with hourly as (
    select rule_id, agent, date_trunc('hour', ts) as hour, count(*) as alerts
    from alerts
    group by 1, 2, 3
),
scored as (
    select *,
        avg(alerts) over (partition by rule_id, agent)         as mean_alerts,
        stddev_samp(alerts) over (partition by rule_id, agent) as sd_alerts
    from hourly
)
select
    hour,
    rule_id,
    (select rule_description from alerts a where a.rule_id = s.rule_id limit 1) as rule_description,
    agent,
    alerts,
    round(mean_alerts, 1) as usual_per_hour,
    round((alerts - mean_alerts) / nullif(sd_alerts, 0), 1) as z_score
from scored s
where (alerts - mean_alerts) / nullif(sd_alerts, 0) > 5
order by z_score desc
limit 15;
```

| hour | rule_id | rule_description | agent | alerts | usual_per_hour | z_score |
|:---|:---|:---|:---|---:|---:|---:|
| 2026-08-24 22:00 | 31101 | Web server 400 error code | web-01 | 916 | 19.6 | 24.8 |
| 2026-08-10 03:00 | 5716 | sshd: authentication failed | vpn-01 | 421 | 3.2 | 22.8 |
| 2026-08-24 22:00 | 31533 | Web attack: SQL injection attempt | web-01 | 36 | 1.5 | 15.6 |
| 2026-08-04 03:00 | 60122 | Windows logon failure | ws-006 | 7 | 1.2 | 9.2 |
| 2026-08-11 03:00 | 5716 | sshd: authentication failed | web-01 | 16 | 2.4 | 7.8 |
| 2026-08-11 03:00 | 60122 | Windows logon failure | ws-005 | 5 | 1.2 | 7.6 |
| 2026-08-11 03:00 | 5710 | sshd: Attempt to login using a non-existent user | app-02 | 11 | 1.8 | 7.5 |
| 2026-08-25 02:00 | 80710 | Auditd: SELinux denied access | app-02 | 9 | 1.6 | 7.2 |
| 2026-08-04 02:00 | 5716 | sshd: authentication failed | app-02 | 15 | 2.5 | 6.9 |
| 2026-08-18 03:00 | 60122 | Windows logon failure | ws-035 | 6 | 1.3 | 6.9 |
| 2026-08-18 02:00 | 5716 | sshd: authentication failed | db-01 | 14 | 2.3 | 6.9 |
| 2026-08-11 02:00 | 80710 | Auditd: SELinux denied access | app-01 | 8 | 1.6 | 6.9 |
| 2026-08-11 02:00 | 5716 | sshd: authentication failed | web-01 | 14 | 2.4 | 6.6 |
| 2026-08-18 02:00 | 60122 | Windows logon failure | ws-020 | 5 | 1.2 | 6.6 |
| 2026-08-04 08:00 | 60122 | Windows logon failure | ws-021 | 5 | 1.3 | 6.6 |

_15 rows._
