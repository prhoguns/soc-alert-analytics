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
