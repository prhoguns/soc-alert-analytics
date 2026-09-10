# Q8. External source IPs by alert count, distinct rules triggered, and hosts touched.

```sql
-- Q8. External source IPs by alert count, distinct rules triggered, and hosts touched.
-- An IP hitting many rules across several hosts is more interesting than one hitting one rule a lot.
select
    src_ip,
    count(*)                    as alerts,
    count(distinct rule_id)     as distinct_rules,
    count(distinct agent)       as hosts_touched,
    min(ts)                     as first_seen,
    max(ts)                     as last_seen,
    max(level)                  as max_level
from alerts
where src_ip is not null and not src_ip like '10.%'
group by 1
order by distinct_rules desc, alerts desc
limit 15;
```

| src_ip | alerts | distinct_rules | hosts_touched | first_seen | last_seen | max_level |
|:---|---:|---:|---:|:---|:---|---:|
| 185.220.104.63 | 733 | 10 | 2 | 2026-08-01 00:05 | 2026-08-30 23:10 | 10 |
| 185.220.109.72 | 709 | 10 | 2 | 2026-08-01 06:12 | 2026-08-30 23:02 | 10 |
| 185.220.101.174 | 704 | 10 | 2 | 2026-08-01 05:07 | 2026-08-30 21:34 | 10 |
| 185.220.104.40 | 676 | 10 | 2 | 2026-08-01 03:19 | 2026-08-30 23:24 | 10 |
| 185.220.106.88 | 674 | 10 | 2 | 2026-08-01 01:42 | 2026-08-30 21:00 | 10 |
| 185.220.109.109 | 690 | 9 | 2 | 2026-08-01 04:32 | 2026-08-30 21:37 | 10 |
| 185.220.109.7 | 687 | 9 | 2 | 2026-08-01 02:40 | 2026-08-30 18:16 | 10 |
| 185.220.100.8 | 665 | 9 | 2 | 2026-08-01 00:48 | 2026-08-30 23:54 | 10 |
| 185.220.103.36 | 663 | 9 | 2 | 2026-08-01 00:34 | 2026-08-30 23:44 | 10 |
| 185.220.102.179 | 637 | 9 | 2 | 2026-08-01 00:08 | 2026-08-30 22:00 | 10 |
| 185.220.103.130 | 636 | 9 | 2 | 2026-08-01 04:21 | 2026-08-30 22:47 | 10 |
| 185.220.108.108 | 690 | 8 | 2 | 2026-08-01 01:12 | 2026-08-30 22:52 | 10 |
| 185.220.108.51 | 690 | 8 | 2 | 2026-08-01 00:22 | 2026-08-30 23:36 | 10 |
| 185.220.100.195 | 687 | 8 | 2 | 2026-08-01 00:02 | 2026-08-30 22:44 | 10 |
| 185.220.101.56 | 681 | 8 | 2 | 2026-08-01 01:38 | 2026-08-30 23:03 | 10 |

_15 rows._
