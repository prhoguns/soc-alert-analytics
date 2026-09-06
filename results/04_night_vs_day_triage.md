# Q4. Does time-to-triage degrade overnight? (Hour the alert fired, in UTC.)

```sql
-- Q4. Does time-to-triage degrade overnight? (Hour the alert fired, in UTC.)
select
    extract(hour from a.ts)::int as hour_fired,
    count(*) as triaged,
    round(avg(date_diff('second', a.ts, tr.opened_at::timestamptz) / 60.0), 1) as mean_min_to_triage,
    round(quantile_cont(date_diff('second', a.ts, tr.opened_at::timestamptz) / 60.0, 0.9), 1) as p90_min_to_triage
from triage tr join alerts a using (alert_id)
where a.level >= 7
group by 1
order by 1;
```

| hour_fired | triaged | mean_min_to_triage | p90_min_to_triage |
|---:|---:|---:|---:|
| 0 | 85 | 130.2 | 282.8 |
| 1 | 74 | 101.4 | 291.9 |
| 2 | 158 | 159.7 | 413.3 |
| 3 | 179 | 120 | 283.1 |
| 4 | 67 | 119.4 | 221.8 |
| 5 | 61 | 129.6 | 274.1 |
| 6 | 67 | 124.9 | 245.6 |
| 7 | 56 | 43 | 91.6 |
| 8 | 145 | 40.5 | 95 |
| 9 | 126 | 36.4 | 82.3 |
| 10 | 134 | 48.9 | 119 |
| 11 | 141 | 40.8 | 113.8 |
| 12 | 140 | 39.7 | 98.6 |
| 13 | 133 | 46.8 | 117.9 |
| 14 | 113 | 42.2 | 96.4 |
| 15 | 138 | 41.7 | 98.1 |
| 16 | 142 | 39.1 | 95.6 |
| 17 | 137 | 47.6 | 114.4 |
| 18 | 64 | 48.5 | 128.1 |
| 19 | 62 | 48 | 105 |
| 20 | 73 | 48.5 | 133.1 |
| 21 | 79 | 43.2 | 117.9 |
| 22 | 64 | 35.4 | 75 |
| 23 | 74 | 145.7 | 345.7 |

_24 rows._
