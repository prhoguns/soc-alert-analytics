"""Generate 30 days of realistic Wazuh-style alerts plus an analyst triage log.

Why synthetic: real SIEM exports contain hostnames, usernames and IPs that should not be
published. The generator reproduces the *shape* of a small SOC's alert stream - business-hours
volume, a handful of rules that produce most of the noise, weekly patching storms, and a few
planted attack scenarios - so the analysis queries have something realistic to find.

Output:
  data/alerts.jsonl   one Wazuh alert JSON object per line (same field names as alerts.json)
  data/triage.csv     analyst actions for the alerts that were opened
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)
START = datetime(2026, 8, 1)
DAYS = 30

AGENTS = (
    [f"ws-{i:03d}" for i in range(1, 41)]
    + ["dc-01", "dc-02", "fs-01", "app-01", "app-02", "db-01", "vpn-01", "web-01", "jump-01"]
)
SERVERS = {"dc-01", "dc-02", "fs-01", "app-01", "app-02", "db-01", "vpn-01", "web-01", "jump-01"}
USERS = [f"user{i:02d}" for i in range(1, 61)] + ["svc-backup", "svc-scan", "administrator"]
EXTERNAL_IPS = [f"185.220.{random.randint(100, 110)}.{random.randint(1, 254)}" for _ in range(20)]

# (rule_id, level, description, mitre_id, tactic, base_rate_per_hour, tp_rate)
# tp_rate is the probability an analyst marks it a true positive - this is what makes some rules "noise".
RULES = [
    ("5710", 5, "sshd: Attempt to login using a non-existent user", "T1110", "Credential Access", 6.0, 0.02),
    ("5716", 5, "sshd: authentication failed", "T1110", "Credential Access", 9.0, 0.02),
    ("5763", 10, "sshd: brute force trying to get access to the system", "T1110", "Credential Access", 0.15, 0.35),
    ("60122", 5, "Windows logon failure", "T1110", "Credential Access", 12.0, 0.01),
    ("60106", 7, "Windows: User account locked out", "T1110", "Credential Access", 0.6, 0.10),
    ("60204", 8, "Windows: New user account created", "T1136", "Persistence", 0.05, 0.40),
    ("60207", 9, "Windows: User added to Administrators group", "T1098", "Privilege Escalation", 0.02, 0.60),
    ("92052", 12, "Sysmon: Suspicious PowerShell encoded command", "T1059.001", "Execution", 0.08, 0.30),
    ("92100", 10, "Sysmon: Mimikatz-like LSASS access", "T1003.001", "Credential Access", 0.01, 0.85),
    ("92200", 8, "Sysmon: Scheduled task created", "T1053.005", "Persistence", 0.3, 0.08),
    ("31101", 5, "Web server 400 error code", "T1190", "Initial Access", 15.0, 0.01),
    ("31151", 10, "Multiple web server 400 error codes from same source ip", "T1190", "Initial Access", 0.2, 0.25),
    ("31533", 6, "Web attack: SQL injection attempt", "T1190", "Initial Access", 0.4, 0.15),
    ("100010", 7, "Suricata: ET SCAN Nmap scripting engine", "T1046", "Discovery", 0.5, 0.05),
    ("100020", 12, "Suricata: ET MALWARE Cobalt Strike beacon", "T1071", "Command and Control", 0.005, 0.90),
    ("100030", 9, "Suricata: ET POLICY DNS query to newly registered domain", "T1568", "Command and Control", 0.3, 0.05),
    ("550", 7, "Integrity checksum changed (FIM)", "T1565", "Impact", 2.0, 0.02),
    ("554", 5, "File added to the system (FIM)", "T1565", "Impact", 3.0, 0.01),
    ("2502", 10, "syslog: User missed the password more than one time", "T1110", "Credential Access", 0.2, 0.05),
    ("80710", 3, "Auditd: SELinux denied access", "", "", 4.0, 0.00),
    ("18107", 5, "Windows: Service startup type changed", "T1543", "Persistence", 0.8, 0.03),
    ("40111", 8, "Multiple authentication failures followed by a success", "T1110", "Credential Access", 0.03, 0.55),
]
ANALYSTS = ["a.okafor", "j.tremblay", "m.singh", "p.rhoguns"]


def hourly_multiplier(ts: datetime) -> float:
    """Business-hours shape: more endpoint noise 8-18 on weekdays, patching storm Tuesday 02:00-04:00."""
    m = 1.0
    if ts.weekday() < 5 and 8 <= ts.hour < 18:
        m *= 2.2
    if ts.weekday() >= 5:
        m *= 0.5
    if ts.weekday() == 1 and 2 <= ts.hour < 4:  # Tuesday patch window
        m *= 6.0
    return m


_seq = 0


def alert(ts: datetime, rule, agent: str, **extra) -> dict:
    global _seq
    _seq += 1
    rule_id, level, desc, mitre_id, tactic, _, _ = rule
    a = {
        "id": f"{int(ts.timestamp())}.{_seq}",  # same shape as Wazuh's alert id
        "timestamp": ts.isoformat(timespec="milliseconds") + "+0000",
        "rule": {"id": rule_id, "level": level, "description": desc, "groups": [desc.split(":")[0].lower()]},
        "agent": {"id": f"{AGENTS.index(agent) + 1:03d}", "name": agent},
        "manager": {"name": "wazuh-manager"},
        "data": {},
        "location": "EventChannel" if agent.startswith(("ws-", "dc-", "fs-", "app-")) else "/var/log/auth.log",
    }
    if mitre_id:
        a["rule"]["mitre"] = {"id": [mitre_id], "tactic": [tactic]}
    a["data"].update(extra)
    return a


def background(out) -> int:
    n = 0
    ts = START
    end = START + timedelta(days=DAYS)
    while ts < end:
        mult = hourly_multiplier(ts)
        for rule in RULES:
            rate = rule[5] * mult
            # FIM storms only during patching; web rules only on web hosts; windows rules only on windows hosts
            if rule[0] in ("550", "554") and not (ts.weekday() == 1 and 2 <= ts.hour < 4):
                rate *= 0.15
            k = _poisson(rate)
            for _ in range(k):
                if rule[0].startswith("31"):
                    agent = "web-01"
                elif rule[0].startswith(("57", "2502", "80710")):
                    agent = random.choice(["vpn-01", "web-01", "jump-01", "app-01", "app-02", "db-01"])
                elif rule[0].startswith("1000"):
                    agent = random.choice(AGENTS)
                else:
                    agent = random.choice([a for a in AGENTS if a not in ("vpn-01", "web-01")])
                t = ts + timedelta(seconds=random.randint(0, 3599))
                out.write(json.dumps(alert(t, rule, agent, srcuser=random.choice(USERS), srcip=_ip(agent))) + "\n")
                n += 1
        ts += timedelta(hours=1)
    return n


def _ip(agent: str) -> str:
    if agent in ("vpn-01", "web-01") and random.random() < 0.7:
        return random.choice(EXTERNAL_IPS)
    return f"10.10.{random.randint(1, 4)}.{random.randint(10, 250)}"


def _poisson(lam: float) -> int:
    # Knuth; fine for small lambda
    import math

    L, k, p = math.exp(-lam), 0, 1.0
    while True:
        k += 1
        p *= random.random()
        if p <= L:
            return k - 1


def scenarios(out) -> list[dict]:
    """Planted attacks. Returns the alerts so triage can mark them true positive."""
    planted = []
    r = {x[0]: x for x in RULES}

    # Scenario 1: SSH brute force from one external IP against vpn-01, day 9, 03:10-03:40, then a success.
    t0 = START + timedelta(days=9, hours=3, minutes=10)
    ip = "185.220.101.44"
    for i in range(420):
        planted.append(alert(t0 + timedelta(seconds=i * 4), r["5716"], "vpn-01", srcip=ip, srcuser="admin"))
    planted.append(alert(t0 + timedelta(minutes=29), r["5763"], "vpn-01", srcip=ip))
    planted.append(alert(t0 + timedelta(minutes=31), r["40111"], "vpn-01", srcip=ip, srcuser="svc-backup"))

    # Scenario 2: lateral movement on day 16 - encoded PowerShell on ws-017, LSASS access, new admin, scheduled task on dc-01.
    t0 = START + timedelta(days=16, hours=14, minutes=22)
    planted.append(alert(t0, r["92052"], "ws-017", srcuser="user23"))
    planted.append(alert(t0 + timedelta(minutes=6), r["92100"], "ws-017", srcuser="user23"))
    planted.append(alert(t0 + timedelta(minutes=41), r["60204"], "dc-01", srcuser="user23", dstuser="helpdesk2"))
    planted.append(alert(t0 + timedelta(minutes=43), r["60207"], "dc-01", srcuser="user23", dstuser="helpdesk2"))
    planted.append(alert(t0 + timedelta(minutes=58), r["92200"], "dc-01", srcuser="helpdesk2"))
    for i in range(6):
        planted.append(alert(t0 + timedelta(hours=1 + i), r["100020"], "ws-017", srcip="10.10.2.117", dstip="45.133.1.9"))

    # Scenario 3: web scanning + SQLi on day 23 from a single IP.
    t0 = START + timedelta(days=23, hours=22)
    ip = "185.220.104.201"
    for i in range(900):
        planted.append(alert(t0 + timedelta(seconds=i * 2), r["31101"], "web-01", srcip=ip))
    for i in range(35):
        planted.append(alert(t0 + timedelta(seconds=300 + i * 17), r["31533"], "web-01", srcip=ip))
    planted.append(alert(t0 + timedelta(minutes=5), r["31151"], "web-01", srcip=ip))

    for a in planted:
        out.write(json.dumps(a) + "\n")
    return planted


def triage(alerts_path: Path, planted: list[dict], out_path: Path) -> int:
    """Analysts open every alert of level >= 7 and a 5% sample of the rest. Time-to-triage depends on
    severity and whether it landed on a night shift; disposition follows each rule's tp_rate, except
    planted alerts which are always true positives."""
    tp_by_rule = {x[0]: x[6] for x in RULES}
    planted_ids = {a["id"] for a in planted}
    n = 0
    with alerts_path.open() as fh, out_path.open("w", newline="") as out:
        w = csv.writer(out)
        w.writerow(["alert_id", "opened_at", "closed_at", "analyst", "disposition", "escalated"])
        for line in fh:
            a = json.loads(line)
            level = a["rule"]["level"]
            if level < 7 and random.random() > 0.05:
                continue
            ts = datetime.fromisoformat(a["timestamp"].replace("+0000", ""))
            night = ts.hour < 7 or ts.hour >= 23
            base = {12: 8, 10: 15, 9: 25, 8: 40, 7: 60}.get(level, 120)
            open_delay = random.expovariate(1 / (base * (3 if night else 1)))
            work = random.expovariate(1 / (10 if level >= 10 else 6))
            opened = ts + timedelta(minutes=open_delay)
            closed = opened + timedelta(minutes=work)
            if a["id"] in planted_ids:
                disp = "true_positive"
            else:
                p = tp_by_rule[a["rule"]["id"]]
                disp = "true_positive" if random.random() < p else random.choice(["false_positive"] * 3 + ["benign"])
            escalated = disp == "true_positive" and level >= 9
            w.writerow([a["id"], opened.isoformat(timespec="seconds"), closed.isoformat(timespec="seconds"),
                        random.choice(ANALYSTS), disp, escalated])
            n += 1
    return n


def main() -> None:
    Path("data").mkdir(exist_ok=True)
    alerts_path = Path("data/alerts.jsonl")
    with alerts_path.open("w") as out:
        n_bg = background(out)
        planted = scenarios(out)
    n_tri = triage(alerts_path, planted, Path("data/triage.csv"))
    # Ground truth for evaluating detection methods (the ml/ module uses this; the SQL never does).
    json.dump(
        {"planted_alert_ids": [a["id"] for a in planted],
         "incidents": {"ssh_brute_force_vpn01": "2026-08-10T03", "lateral_movement_ws017_dc01": "2026-08-17T14", "web_scan_sqli_web01": "2026-08-24T22"}},
        Path("data/planted.json").open("w"),
    )
    print(f"alerts: {n_bg + len(planted):,} ({len(planted)} planted)  triage rows: {n_tri:,}")


if __name__ == "__main__":
    main()
