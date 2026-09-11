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
