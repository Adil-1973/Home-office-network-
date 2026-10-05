"""Back up running-configs (secrets masked) to backups/<device>/<timestamp>.txt"""
from datetime import datetime
from common import ROOT, load_inventory, connect, mask_secrets

def main():
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for d in load_inventory()["devices"]:
        try:
            with connect(d) as conn:
                conn.enable()
                cfg = mask_secrets(conn.send_command("show running-config"))
            folder = ROOT / "backups" / d["name"]
            folder.mkdir(parents=True, exist_ok=True)
            (folder / f"{stamp}.txt").write_text(cfg)
            print(f"[ok] {d['name']} backed up")
        except Exception as e:
            print(f"[FAIL] {d['name']}: {e}")

if __name__ == "__main__":
    main()
