from __future__ import annotations
import json
import keyring
from platformdirs import user_config_dir
from pathlib import Path

CONFIG_FILE = Path(user_config_dir("PDV-SAT-Pro", "GCNB")) / "fiscal.json"
KEYRING_SERVICE = "GCNB.PDV-SAT-Pro"
SECRET_KEYS = ("sat_code", "nfce_password", "nfce_csc")

DEFAULTS = {
    "fiscal_type": "SAT", "environment": "homologacao", "uf": "SP",
    "cnpj": "", "ie": "", "sat_dll": "", "sat_code": "", "sat_number": "1",
    "nfce_certificate": "", "nfce_password": "", "nfce_csc": "", "nfce_csc_id": "1",
    "nfce_series": "1", "nfce_last_number": "0", "max_discount_percent": "20",
    "company_name": "GCNB LTDA", "operator_name": "ADMIN", "report_role": "ADMIN",
    "printer_name": "", "printer_paper": "80", "printer_copies": "1",
    "printer_auto": False, "printer_header": "", "printer_footer": "Obrigado pela preferência"
}

def load_settings():
    try:
        values = DEFAULTS | json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        values = DEFAULTS.copy()
    for key in SECRET_KEYS:
        try:
            values[key] = keyring.get_password(KEYRING_SERVICE, key) or ""
        except keyring.errors.KeyringError:
            values[key] = ""
    return values

def save_settings(values):
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    public = DEFAULTS | values
    for key in SECRET_KEYS:
        secret = str(public.pop(key, ""))
        try:
            if secret: keyring.set_password(KEYRING_SERVICE, key, secret)
            else: keyring.delete_password(KEYRING_SERVICE, key)
        except (keyring.errors.KeyringError, keyring.errors.PasswordDeleteError) as exc:
            raise RuntimeError("Não foi possível acessar o cofre seguro do sistema.") from exc
    CONFIG_FILE.write_text(json.dumps(public, ensure_ascii=False, indent=2), encoding="utf-8")

def validate_fiscal_settings(values):
    required = ["cnpj", "ie", "uf"]
    if values.get("fiscal_type") == "SAT": required += ["sat_dll", "sat_code"]
    else: required += ["nfce_certificate", "nfce_password", "nfce_csc", "nfce_csc_id", "nfce_series"]
    missing = [key for key in required if not str(values.get(key, "")).strip()]
    if values.get("environment") == "producao" and missing:
        raise ValueError("Produção exige: " + ", ".join(missing))
    return True
