-- Q12. What would volume look like if the 'TUNE' rules from Q2 (over 2,000 alerts, under 3% true-positive) were suppressed?
with tune as (
    select a.rule_id
    from alerts a
    left join triage t using (alert_id)
    group by 1
    having count(*) > 2000
       and count(t.alert_id) filter (where t.disposition = 'true_positive') * 1.0 / nullif(count(t.alert_id), 0) < 0.03
),
weekly as (
    select
        date_trunc('week', ts)::date as week,
        count(*) as alerts,
        count(*) filter (where rule_id not in (select rule_id from tune)) as alerts_after_tuning
    from alerts
    group by 1
)
select
    week,
    alerts,
    alerts_after_tuning,
    round(100.0 * (alerts - alerts_after_tuning) / alerts, 1) as pct_reduction
from weekly
order by 1;
