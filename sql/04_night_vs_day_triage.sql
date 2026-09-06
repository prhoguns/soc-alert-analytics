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
