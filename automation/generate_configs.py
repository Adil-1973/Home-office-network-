"""Render device configs from inventory.yaml + Jinja2 templates -> configs/*.txt"""
from jinja2 import Environment, FileSystemLoader
from common import ROOT, load_inventory

def main():
    inv = load_inventory()
    env = Environment(loader=FileSystemLoader(ROOT / "templates"),
                      trim_blocks=True, lstrip_blocks=True)
    out_dir = ROOT / "configs"
    out_dir.mkdir(exist_ok=True)
    for d in inv["devices"]:
        text = env.get_template(f"{d['type']}.j2").render(d=d, **inv)
        (out_dir / f"{d['name']}.txt").write_text(text)
        print(f"[ok] configs/{d['name']}.txt")

if __name__ == "__main__":
    main()
