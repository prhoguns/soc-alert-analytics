# Q2. The tuning report: which rules generate the most alerts, and how often are they real?

```sql
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
```

| rule_id | rule_description | level | alerts | pct_of_all_alerts | triaged | tp_rate_pct | fp_rate_pct | recommendation |
|:---|:---|---:|---:|---:|---:|---:|---:|:---|
| 31101 | Web server 400 error code | 5 | 14,137 | 30.8 | 701 | 8.7 | 68 | review |
| 60122 | Windows logon failure | 5 | 10,491 | 22.9 | 505 | 1 | 72.1 | TUNE: high volume, ~never true |
| 5716 | sshd: authentication failed | 5 | 8,229 | 18 | 414 | 7.2 | 73.9 | review |
| 5710 | sshd: Attempt to login using a non-existent user | 5 | 5,316 | 11.6 | 244 | 0.8 | 73.4 | TUNE: high volume, ~never true |
| 80710 | Auditd: SELinux denied access | 3 | 3,427 | 7.5 | 183 | 0 | 70.5 | TUNE: high volume, ~never true |
| 18107 | Windows: Service startup type changed | 5 | 780 | 1.7 | 49 | 2 | 77.6 | review |
| 554 | File added to the system (FIM) | 5 | 556 | 1.2 | 20 | 0 | 65 | review |
| 60106 | Windows: User account locked out | 7 | 511 | 1.1 | 511 | 10.2 | 67.1 | review |
| 100010 | Suricata: ET SCAN Nmap scripting engine | 7 | 399 | 0.9 | 399 | 8.5 | 72.2 | review |
| 31533 | Web attack: SQL injection attempt | 6 | 391 | 0.9 | 19 | 15.8 | 68.4 | review |
| 550 | Integrity checksum changed (FIM) | 7 | 332 | 0.7 | 332 | 2.4 | 76.8 | review |
| 100030 | Suricata: ET POLICY DNS query to newly registered domain | 9 | 313 | 0.7 | 313 | 6.4 | 71.2 | review |
| 92200 | Sysmon: Scheduled task created | 8 | 287 | 0.6 | 287 | 8.4 | 71.1 | review |
| 2502 | syslog: User missed the password more than one time | 10 | 173 | 0.4 | 173 | 2.3 | 74.6 | review |
| 31151 | Multiple web server 400 error codes from same source ip | 10 | 162 | 0.4 | 162 | 26.5 | 56.8 | review |
| 5763 | sshd: brute force trying to get access to the system | 10 | 112 | 0.2 | 112 | 40.2 | 37.5 | review |
| 92052 | Sysmon: Suspicious PowerShell encoded command | 12 | 93 | 0.2 | 93 | 31.2 | 47.3 | review |
| 60204 | Windows: New user account created | 8 | 58 | 0.1 | 58 | 43.1 | 44.8 | review |
| 40111 | Multiple authentication failures followed by a success | 8 | 22 | 0 | 22 | 77.3 | 22.7 | KEEP: high fidelity |
| 92100 | Sysmon: Mimikatz-like LSASS access | 10 | 19 | 0 | 19 | 100 | 0 | KEEP: high fidelity |
| 60207 | Windows: User added to Administrators group | 9 | 18 | 0 | 18 | 72.2 | 22.2 | KEEP: high fidelity |
| 100020 | Suricata: ET MALWARE Cobalt Strike beacon | 12 | 13 | 0 | 13 | 92.3 | 7.7 | KEEP: high fidelity |

_22 rows._
