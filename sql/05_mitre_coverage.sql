-- Q5. MITRE ATT&CK coverage: alerts and confirmed true positives per tactic.
-- Tactics with alerts but zero confirmations may be all noise; tactics with no rules at all are blind spots.
with all_tactics as (
    select unnest(['Initial Access','Execution','Persistence','Privilege Escalation','Defense Evasion','Credential Access',
                   'Discovery','Lateral Movement','Collection','Command and Control','Exfiltration','Impact']) as tactic
),
stats as (
    select
        a.mitre_tactic as tactic,
        count(*) as alerts,
        count(distinct a.rule_id) as rules,
        count(*) filter (where t.disposition = 'true_positive') as confirmed
    from alerts a left join triage t using (alert_id)
    where a.mitre_tactic is not null
    group by 1
)
select
    at.tactic,
    coalesce(s.rules, 0) as rules,
    coalesce(s.alerts, 0) as alerts,
    coalesce(s.confirmed, 0) as confirmed_true_positives,
    case when s.rules is null then 'BLIND SPOT: no detection rule'
         when s.confirmed = 0 then 'no confirmed detections in 30 days'
         else 'covered' end as status
from all_tactics at
left join stats s using (tactic)
order by alerts desc;
