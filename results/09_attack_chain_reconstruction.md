# Q9. Reconstruct multi-stage activity: starting from any level>=8 alert, collect every level>=8 alert on the

```sql
-- Q9. Reconstruct multi-stage activity: starting from any level>=8 alert, collect every level>=8 alert on the
-- same host OR by the same user in the next 2 hours, and count distinct MITRE tactics. Single alerts are noise;
-- a sequence of tactics is an incident. The planted lateral-movement chain should rank first.
with anchors as (
    select alert_id, agent, src_user, ts
    from alerts
    where level >= 8 and mitre_tactic is not null
),
chains as (
    select
        an.alert_id,
        an.agent,
        an.src_user,
        an.ts                                         as window_start,
        max(a2.ts)                                    as window_end,
        count(distinct a2.mitre_tactic)               as tactics_in_window,
        count(distinct a2.agent)                      as hosts_in_window,
        string_agg(distinct a2.mitre_tactic, ' | ')   as tactics_seen
    from anchors an
    join alerts a2
      on (a2.agent = an.agent or a2.src_user = an.src_user)
     and a2.level >= 8
     and a2.mitre_tactic is not null
     and a2.ts between an.ts and an.ts + interval 2 hour
    group by 1, 2, 3, 4
)
select agent as first_host, src_user, window_start, window_end, tactics_in_window, hosts_in_window, tactics_seen
from chains
where tactics_in_window >= 3
order by tactics_in_window desc, hosts_in_window desc, window_start
limit 10;
```

| first_host | src_user | window_start | window_end | tactics_in_window | hosts_in_window | tactics_seen |
|:---|:---|:---|:---|---:|---:|:---|
| ws-017 | user23 | 2026-08-17 14:22 | 2026-08-17 16:22 | 5 | 2 | Command and Control | Persistence | Privilege Escalation | Execution | Credential Access |
| ws-017 | user23 | 2026-08-17 14:28 | 2026-08-17 16:22 | 4 | 2 | Command and Control | Credential Access | Persistence | Privilege Escalation |
| web-01 | user34 | 2026-08-04 02:28 | 2026-08-04 03:45 | 3 | 3 | Credential Access | Persistence | Initial Access |
| ws-024 | user48 | 2026-08-07 08:24 | 2026-08-07 10:14 | 3 | 3 | Credential Access | Command and Control | Persistence |
| ws-028 | user54 | 2026-08-18 01:04 | 2026-08-18 02:41 | 3 | 3 | Persistence | Command and Control | Credential Access |
| web-01 | user58 | 2026-08-03 14:04 | 2026-08-03 15:58 | 3 | 2 | Credential Access | Initial Access | Persistence |
| jump-01 | user33 | 2026-08-04 03:08 | 2026-08-04 05:03 | 3 | 2 | Command and Control | Credential Access | Persistence |
| ws-034 | user01 | 2026-08-05 06:53 | 2026-08-05 08:34 | 3 | 2 | Command and Control | Execution | Persistence |
| ws-034 | user01 | 2026-08-05 06:54 | 2026-08-05 08:34 | 3 | 2 | Execution | Command and Control | Persistence |
| web-01 | user56 | 2026-08-06 01:18 | 2026-08-06 02:41 | 3 | 2 | Persistence | Initial Access | Credential Access |

_10 rows._
