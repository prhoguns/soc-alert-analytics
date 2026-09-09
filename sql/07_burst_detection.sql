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
