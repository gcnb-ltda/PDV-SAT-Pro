from __future__ import annotations
import json
from pathlib import Path

CONFIG_FILE = Path.home() / ".pdv_sat_pro" / "fiscal.json"

DEFAULTS = {
    "fiscal_type": "SAT", "environment": "homologacao", "uf": "SP",
    "cnpj": "", "ie": "", "sat_dll": "", "sat_code": "", "sat_number": "1",
    "nfce_certificate": "", "nfce_password": "", "nfce_csc": "", "nfce_csc_id": "1",
    "nfce_series": "1", "nfce_last_number": "0"
}

def load_settings():
    try:
        return DEFAULTS | json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULTS.copy()

def save_settings(values):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(DEFAULTS | values, ensure_ascii=False, indent=2), encoding="utf-8")

