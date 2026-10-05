"""Shared helpers: inventory loading, Netmiko connection, secret masking."""
import os, re, yaml
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

def load_inventory():
    with open(ROOT / "inventory.yaml") as f:
        return yaml.safe_load(f)

def connect(device):
    from netmiko import ConnectHandler  # imported lazily so config generation needs no netmiko
    return ConnectHandler(
        device_type="cisco_ios",
        host=device["mgmt_ip"],
        username=os.environ["NET_USER"],
        password=os.environ["NET_PASS"],
        secret=os.environ.get("NET_SECRET", ""),
    )

SECRET_PATTERNS = [
    (re.compile(r"\b(secret|password)\s+\d\s+\S+", re.I), r"\1 <REDACTED>"),
    (re.compile(r"(snmp-server community)\s+\S+", re.I), r"\1 <REDACTED>"),
    (re.compile(r"\b(key)\s+\d\s+\S+", re.I), r"\1 <REDACTED>"),
]

def mask_secrets(text):
    for pattern, repl in SECRET_PATTERNS:
        text = pattern.sub(repl, text)
    return text
