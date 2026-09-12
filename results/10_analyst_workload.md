# Q10. Per-analyst workload and outcomes. Big differences in FP rate between analysts usually mean inconsistent triage criteria, not skill.

```sql
-- Q10. Per-analyst workload and outcomes. Big differences in FP rate between analysts usually mean inconsistent triage criteria, not skill.
select
    analyst,
    count(*) as alerts_closed,
    round(avg(date_diff('second', opened_at, closed_at) / 60.0), 1) as mean_min_per_alert,
    round(100.0 * count(*) filter (where disposition = 'true_positive') / count(*), 1) as tp_pct,
    round(100.0 * count(*) filter (where disposition = 'false_positive') / count(*), 1) as fp_pct,
    count(*) filter (where escalated) as escalations
from triage
group by 1
order by alerts_closed desc;
```

| analyst | alerts_closed | mean_min_per_alert | tp_pct | fp_pct | escalations |
|:---|---:|---:|---:|---:|---:|
| m.singh | 1,240 | 6.2 | 8.4 | 67.7 | 45 |
| p.rhoguns | 1,149 | 6.4 | 9.8 | 68.8 | 46 |
| a.okafor | 1,140 | 6.3 | 10.3 | 68.5 | 47 |
| j.tremblay | 1,118 | 6.5 | 10.1 | 68.3 | 47 |

_4 rows._
