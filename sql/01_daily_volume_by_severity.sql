-- Q1. Daily alert volume by severity band. Is the load stable or spiky?
-- Wazuh levels: 0-6 low, 7-9 medium, 10-11 high, 12+ critical.
select
    ts::date as day,
    count(*) filter (where level <= 6)             as low,
    count(*) filter (where level between 7 and 9)  as medium,
    count(*) filter (where level between 10 and 11) as high,
    count(*) filter (where level >= 12)            as critical,
    count(*)                                        as total
from alerts
group by 1
order by 1;
