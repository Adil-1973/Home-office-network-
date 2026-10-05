"""Push generated configs to devices. Dry-run by default; use --apply to push."""
import argparse
from common import ROOT, load_inventory, connect

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="actually push the config")
    ap.add_argument("--only", help="deploy a single device by name")
    args = ap.parse_args()

    for d in load_inventory()["devices"]:
        if args.only and d["name"] != args.only:
            continue
        lines = (ROOT / "configs" / f"{d['name']}.txt").read_text().splitlines()
        if not args.apply:
            print(f"[dry-run] {d['name']}: {len(lines)} lines would be pushed")
            continue
        try:
            with connect(d) as conn:
                conn.enable()
                conn.send_config_set(lines)
                conn.save_config()
            print(f"[ok] {d['name']} configured and saved")
        except Exception as e:
            print(f"[FAIL] {d['name']}: {e}")

if __name__ == "__main__":
    main()
