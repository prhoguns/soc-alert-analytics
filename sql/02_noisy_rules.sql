-- Q2. The tuning report: which rules generate the most alerts, and how often are they real?
-- A rule with high volume and a near-zero true-positive rate is a tuning candidate.
with vol as (
    select rule_id, rule_description, level, count(*) as alerts
    from alerts group by 1, 2, 3
),
disp as (
    select a.rule_id,
           count(*)                                              as triaged,
           count(*) filter (where t.disposition = 'true_positive') as true_positives,
           count(*) filter (where t.disposition = 'false_positive') as false_positives
    from triage t join alerts a using (alert_id)
    group by 1
)
select
    v.rule_id,
    v.rule_description,
    v.level,
    v.alerts,
    round(100.0 * v.alerts / sum(v.alerts) over (), 1)        as pct_of_all_alerts,
    d.triaged,
    round(100.0 * d.true_positives / nullif(d.triaged, 0), 1) as tp_rate_pct,
    round(100.0 * d.false_positives / nullif(d.triaged, 0), 1) as fp_rate_pct,
    case
        when v.alerts > 2000 and coalesce(d.true_positives, 0) * 1.0 / nullif(d.triaged, 0) < 0.03 then 'TUNE: high volume, ~never true'
        when coalesce(d.true_positives, 0) * 1.0 / nullif(d.triaged, 0) >= 0.5 then 'KEEP: high fidelity'
        else 'review'
    end as recommendation
from vol v
left join disp d using (rule_id)
order by v.alerts desc;
