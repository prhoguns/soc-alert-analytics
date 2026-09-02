"""Load data/alerts.jsonl (Wazuh alerts.json format) and data/triage.csv into data/soc.duckdb.

Works on a real Wazuh export too: copy /var/ossec/logs/alerts/alerts.json to data/alerts.jsonl.
Fields that don't exist in your export simply come through as NULL.
"""
import duckdb

DB = "data/soc.duckdb"


def main() -> None:
    con = duckdb.connect(DB)
    con.execute("drop table if exists alerts")
    con.execute(
        """
        create table alerts as
        select
            id                                                 as alert_id,
            strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%f%z')    as ts,
            rule.id                                            as rule_id,
            rule.level                                         as level,
            rule.description                                   as rule_description,
            try_cast(rule.mitre.id[1] as varchar)              as mitre_technique,
            try_cast(rule.mitre.tactic[1] as varchar)          as mitre_tactic,
            agent.name                                         as agent,
            data.srcip                                         as src_ip,
            data.srcuser                                       as src_user,
            data.dstuser                                       as dst_user,
            location
        from read_json('data/alerts.jsonl', format = 'newline_delimited',
                       columns = {
                         id: 'VARCHAR',
                         timestamp: 'VARCHAR',
                         rule: 'STRUCT(id VARCHAR, level INTEGER, description VARCHAR, groups VARCHAR[], mitre STRUCT(id VARCHAR[], tactic VARCHAR[]))',
                         agent: 'STRUCT(id VARCHAR, name VARCHAR)',
                         manager: 'STRUCT(name VARCHAR)',
                         data: 'STRUCT(srcip VARCHAR, srcuser VARCHAR, dstuser VARCHAR, dstip VARCHAR)',
                         location: 'VARCHAR'
                       })
        """
    )
    con.execute("drop table if exists triage")
    con.execute(
        """
        create table triage as
        select alert_id::varchar as alert_id, opened_at::timestamp as opened_at, closed_at::timestamp as closed_at,
               analyst, disposition, escalated::boolean as escalated
        from read_csv('data/triage.csv', header = true, types = {'alert_id': 'VARCHAR'})
        """
    )
    n = con.execute("select count(*) from alerts").fetchone()[0]
    t = con.execute("select count(*) from triage").fetchone()[0]
    print(f"built {DB}: alerts={n:,} triage={t:,}")


if __name__ == "__main__":
    main()
