-- Q6. Alert volume by weekday and hour. Input for a staffing heatmap.
select
    dayname(ts) as weekday,
    isodow(ts)  as dow_num,
    extract(hour from ts)::int as hour,
    count(*) as alerts
from alerts
group by 1, 2, 3
order by dow_num, hour;
