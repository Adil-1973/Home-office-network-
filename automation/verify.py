"""Check that the live network matches inventory.yaml."""
import re
from common import load_inventory, connect

def check(name, ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    return ok

def main():
    inv = load_inventory()
    all_ok = True
    for d in inv["devices"]:
        print(f"\n== {d['name']} ==")
        try:
            with connect(d) as conn:
                conn.enable()
                vlans = conn.send_command("show vlan brief")
                if d["type"] == "access":
                    expected = [d["vlan"], inv["mgmt"]["id"]]
                else:
                    expected = [v["id"] for v in inv["vlans"]] + [inv["mgmt"]["id"]]
                for vid in expected:
                    found = re.search(rf"^{vid}\s", vlans, re.M) is not None
                    all_ok &= check(f"VLAN {vid} exists", found)
                if d["type"] == "core":
                    brief = conn.send_command("show ip interface brief")
                    for v in inv["vlans"]:
                        line = next((l for l in brief.splitlines()
                                     if l.startswith(f"Vlan{v['id']} ")), "")
                        all_ok &= check(f"SVI Vlan{v['id']} up/up", line.split()[-2:] == ["up", "up"])
                    acls = conn.send_command("show access-lists")
                    for role in inv["deny"]:
                        name = next(v["name"] for v in inv["vlans"] if v["role"] == role)
                        all_ok &= check(f"ACL {name}-IN present", f"{name}-IN" in acls)
                    route = conn.send_command("show ip route 0.0.0.0")
                    all_ok &= check("default route via uplink", inv["uplink"]["next_hop"] in route)
        except Exception as e:
            all_ok = False
            print(f"  [FAIL] cannot connect: {e}")
    print("\nRESULT:", "ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED")

if __name__ == "__main__":
    main()
