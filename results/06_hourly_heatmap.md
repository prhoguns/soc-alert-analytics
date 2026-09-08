# Q6. Alert volume by weekday and hour. Input for a staffing heatmap.

```sql
-- Q6. Alert volume by weekday and hour. Input for a staffing heatmap.
select
    dayname(ts) as weekday,
    isodow(ts)  as dow_num,
    extract(hour from ts)::int as hour,
    count(*) as alerts
from alerts
group by 1, 2, 3
order by dow_num, hour;
```

| weekday | dow_num | hour | alerts |
|:---|---:|---:|---:|
| Monday | 1 | 0 | 211 |
| Monday | 1 | 1 | 197 |
| Monday | 1 | 2 | 186 |
| Monday | 1 | 3 | 638 |
| Monday | 1 | 4 | 220 |
| Monday | 1 | 5 | 188 |
| Monday | 1 | 6 | 185 |
| Monday | 1 | 7 | 185 |
| Monday | 1 | 8 | 503 |
| Monday | 1 | 9 | 415 |
| Monday | 1 | 10 | 466 |
| Monday | 1 | 11 | 461 |
| Monday | 1 | 12 | 448 |
| Monday | 1 | 13 | 427 |
| Monday | 1 | 14 | 438 |
| Monday | 1 | 15 | 462 |
| Monday | 1 | 16 | 459 |
| Monday | 1 | 17 | 443 |
| Monday | 1 | 18 | 190 |
| Monday | 1 | 19 | 172 |
| Monday | 1 | 20 | 182 |
| Monday | 1 | 21 | 218 |
| Monday | 1 | 22 | 1,114 |
| Monday | 1 | 23 | 189 |
| Tuesday | 2 | 0 | 198 |
| Tuesday | 2 | 1 | 223 |
| Tuesday | 2 | 2 | 1,269 |
| Tuesday | 2 | 3 | 1,295 |
| Tuesday | 2 | 4 | 212 |
| Tuesday | 2 | 5 | 196 |
| Tuesday | 2 | 6 | 177 |
| Tuesday | 2 | 7 | 210 |
| Tuesday | 2 | 8 | 465 |
| Tuesday | 2 | 9 | 440 |
| Tuesday | 2 | 10 | 467 |
| Tuesday | 2 | 11 | 442 |
| Tuesday | 2 | 12 | 414 |
| Tuesday | 2 | 13 | 430 |
| Tuesday | 2 | 14 | 424 |
| Tuesday | 2 | 15 | 408 |
| Tuesday | 2 | 16 | 457 |
| Tuesday | 2 | 17 | 419 |
| Tuesday | 2 | 18 | 220 |
| Tuesday | 2 | 19 | 211 |
| Tuesday | 2 | 20 | 205 |
| Tuesday | 2 | 21 | 209 |
| Tuesday | 2 | 22 | 222 |
| Tuesday | 2 | 23 | 195 |
| Wednesday | 3 | 0 | 184 |
| Wednesday | 3 | 1 | 194 |
| Wednesday | 3 | 2 | 186 |
| Wednesday | 3 | 3 | 194 |
| Wednesday | 3 | 4 | 235 |
| Wednesday | 3 | 5 | 191 |
| Wednesday | 3 | 6 | 214 |
| Wednesday | 3 | 7 | 194 |
| Wednesday | 3 | 8 | 454 |
| Wednesday | 3 | 9 | 457 |
| Wednesday | 3 | 10 | 454 |
| Wednesday | 3 | 11 | 475 |

_168 rows; showing first 60._
