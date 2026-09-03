from __future__ import annotations
import json
import hashlib
import keyring
from platformdirs import user_config_dir
from pathlib import Path

CONFIG_FILE = Path(user_config_dir("PDV-SAT-Pro", "GCNB")) / "fiscal.json"
KEYRING_SERVICE = "GCNB.PDV-SAT-Pro"
SECRET_KEYS = ("sat_code", "nfce_password", "nfce_csc")

DEFAULTS = {
    "fiscal_type": "NFC-e", "environment": "homologacao", "uf": "SP",
    "cnpj": "", "ie": "", "sat_dll": "", "sat_code": "", "sat_number": "1",
    "nfce_certificate": "", "nfce_password": "", "nfce_csc": "", "nfce_csc_id": "1",
    "nfce_series": "1", "nfce_last_number": "0", "max_discount_percent": "20",
    "company_name": "", "operator_name": "ADMIN", "report_role": "ADMIN",
    "printer_name": "", "printer_paper": "80", "printer_copies": "1",
    "printer_auto": False, "printer_header": "", "printer_footer": "Obrigado pela preferência",
    "nfce_provider": "SEFAZ Direta", "tax_regime": "3",
    "trade_name":"", "street":"", "address_number":"", "district":"", "cep":"",
    "municipality_code":"", "municipality_name":"", "nfce_qrcode_url":"", "nfce_consult_url":"",
    "schema_dir":"", "sefaz_endpoints_json":"", "nfce_offline_enabled":True,
    "nfce_direct_enabled":False, "sefaz_homologation_approved":False,
    "sefaz_credentialed":False, "sefaz_validation_fingerprint":""
}

VALID_UFS={"AC","AL","AP","AM","BA","CE","DF","ES","GO","MA","MT","MS","MG","PA","PB","PR","PE","PI","RJ","RN","RS","RO","RR","SC","SP","SE","TO"}

def fiscal_fingerprint(values):
    fields=("fiscal_type","environment","uf","cnpj","ie","municipality_code",
            "tax_regime","nfce_certificate","nfce_csc_id","nfce_series",
            "nfce_qrcode_url","nfce_consult_url","schema_dir")
    payload="|".join(str(values.get(key,"")).strip() for key in fields)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

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
    # Em homologação/simulação a tela pode ser salva por etapas. Produção e a
    # ativação do motor direto continuam exigindo configuração completa.
    strict = values.get("environment") == "producao" or values.get("nfce_direct_enabled")
    if strict and str(values.get("uf","")).upper() not in VALID_UFS: raise ValueError("Informe uma UF brasileira válida.")
    if values.get("environment") == "producao" and values.get("fiscal_type") == "SAT": raise ValueError("SAT não está habilitado para produção. Utilize NFC-e.")
    required = ["cnpj", "ie", "uf"]
    if values.get("fiscal_type") == "SAT": required += ["sat_dll", "sat_code"]
    else: required += ["nfce_certificate", "nfce_password", "nfce_csc", "nfce_csc_id", "nfce_series", "street", "address_number", "district", "municipality_code", "municipality_name", "nfce_qrcode_url", "nfce_consult_url", "schema_dir"]
    missing = [key for key in required if not str(values.get(key, "")).strip()]
    if strict and missing:
        raise ValueError("Emissão fiscal real exige: " + ", ".join(missing))
    if values.get("nfce_direct_enabled") and not values.get("sefaz_homologation_approved"):
        raise ValueError("A emissão direta só pode ser ativada após aprovação dos testes de homologação SEFAZ.")
    if values.get("nfce_direct_enabled") and not values.get("sefaz_credentialed"):
        raise ValueError("Confirme que o estabelecimento está credenciado para NFC-e na SEFAZ.")
    if values.get("nfce_direct_enabled") and values.get("sefaz_validation_fingerprint") != fiscal_fingerprint(values):
        raise ValueError("A configuração fiscal mudou. Teste novamente a comunicação SEFAZ antes de ativar.")
    return True
