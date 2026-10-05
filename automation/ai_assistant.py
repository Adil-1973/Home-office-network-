"""AI network assistant powered by Claude.

  python ai_assistant.py review               # security/design review of generated configs
  python ai_assistant.py troubleshoot "Sales cannot reach the internet"
  python ai_assistant.py diff CORE            # explain what changed between last two backups

Secrets are masked before anything is sent to the API.
"""
import sys
import anthropic
from common import ROOT, load_inventory, connect, mask_secrets

MODEL = "claude-sonnet-5-5"
client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

SYSTEM = ("You are a senior network engineer (CCNP level). Be concise and concrete. "
          "Reference exact device names, interfaces and commands. Rank findings by severity. "
          "Never invent output that was not provided.")

def ask(prompt):
    msg = client.messages.create(model=MODEL, max_tokens=1500, system=SYSTEM,
                                 messages=[{"role": "user", "content": prompt}])
    return "".join(b.text for b in msg.content if b.type == "text")

def review():
    blob = ""
    for p in sorted((ROOT / "configs").glob("*.txt")):
        blob += f"\n### {p.stem}\n{mask_secrets(p.read_text())}\n"
    print(ask("Review these configs of a 4-department office network (IT, HR, Admin, Sales). "
              "Find security gaps, misconfigurations and missing best practices (SSH, AAA, "
              "logging, STP, DHCP snooping, stateless ACL return-traffic issues) and give "
              f"fixes as IOS commands.\n{blob}"))

def troubleshoot(symptom):
    cmds = ["show ip interface brief", "show vlan brief", "show ip route",
            "show access-lists", "show interfaces trunk", "show ip dhcp binding"]
    core = next(d for d in load_inventory()["devices"] if d["type"] == "core")
    outputs = ""
    with connect(core) as conn:
        conn.enable()
        for c in cmds:
            outputs += f"\n$ {c}\n{mask_secrets(conn.send_command(c))}\n"
    print(ask(f"Symptom: {symptom}\n\nOutputs from CORE:{outputs}\n\n"
              "Give the most likely root causes in order, the exact command to confirm each, "
              "and the fix."))

def diff(device):
    files = sorted((ROOT / "backups" / device).glob("*.txt"))
    if len(files) < 2:
        sys.exit("Need at least two backups. Run backup.py twice.")
    old, new = files[-2].read_text(), files[-1].read_text()
    print(ask(f"Old config:\n{old}\n\nNew config:\n{new}\n\n"
              "Summarize what changed in plain English, flag risky changes, and say if "
              "anything could cause an outage."))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == "review":
        review()
    elif cmd == "troubleshoot" and len(sys.argv) > 2:
        troubleshoot(" ".join(sys.argv[2:]))
    elif cmd == "diff" and len(sys.argv) > 2:
        diff(sys.argv[2])
    else:
        sys.exit(__doc__)
