# Q11. Gap check: high-severity alerts nobody opened. Should be zero.

```sql
-- Q11. Gap check: high-severity alerts nobody opened. Should be zero.
select
    a.level,
    count(*) as alerts,
    count(t.alert_id) as triaged,
    count(*) - count(t.alert_id) as untriaged,
    round(100.0 * count(t.alert_id) / count(*), 1) as pct_triaged
from alerts a
left join triage t using (alert_id)
where a.level >= 7
group by 1
order by 1 desc;
```

| level | alerts | triaged | untriaged | pct_triaged |
|---:|---:|---:|---:|---:|
| 12 | 106 | 106 | 0 | 100 |
| 10 | 466 | 466 | 0 | 100 |
| 9 | 331 | 331 | 0 | 100 |
| 8 | 367 | 367 | 0 | 100 |
| 7 | 1,242 | 1,242 | 0 | 100 |

_5 rows._
