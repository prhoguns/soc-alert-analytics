# Q3. Mean and p90 time-to-triage (alert fired -> analyst opened) and time-to-close, by severity.

```sql
-- Q3. Mean and p90 time-to-triage (alert fired -> analyst opened) and time-to-close, by severity.
-- SLA assumption: critical within 15 min, high within 30, medium within 60.
with t as (
    select
        a.level,
        case when a.level >= 12 then 'critical' when a.level >= 10 then 'high' when a.level >= 7 then 'medium' else 'low' end as severity,
        date_diff('second', a.ts, tr.opened_at::timestamptz) / 60.0 as minutes_to_open,
        date_diff('second', tr.opened_at::timestamptz, tr.closed_at::timestamptz) / 60.0 as minutes_working
    from triage tr join alerts a using (alert_id)
)
select
    severity,
    count(*)                                   as triaged,
    round(avg(minutes_to_open), 1)             as mean_min_to_triage,
    round(quantile_cont(minutes_to_open, 0.5), 1) as p50_min_to_triage,
    round(quantile_cont(minutes_to_open, 0.9), 1) as p90_min_to_triage,
    round(avg(minutes_working), 1)             as mean_min_working,
    round(100.0 * count(*) filter (
        where minutes_to_open <= case severity when 'critical' then 15 when 'high' then 30 when 'medium' then 60 else 240 end
    ) / count(*), 1)                           as pct_within_sla
from t
group by 1
order by case severity when 'critical' then 1 when 'high' then 2 when 'medium' then 3 else 4 end;
```

| severity | triaged | mean_min_to_triage | p50_min_to_triage | p90_min_to_triage | mean_min_working | pct_within_sla |
|:---|---:|---:|---:|---:|---:|---:|
| critical | 106 | 12.3 | 5.8 | 31.1 | 9.9 | 73.6 |
| high | 466 | 24.1 | 14.4 | 58.3 | 9.5 | 73.2 |
| medium | 1,940 | 83.8 | 45.2 | 193.8 | 5.9 | 58.6 |
| low | 2,135 | 181.3 | 108.6 | 415.4 | 5.8 | 76.4 |

_4 rows._
