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
