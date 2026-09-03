from settings import load_settings,validate_fiscal_settings
from sat import create_sat
from nfce import create_nfce

def create_fiscal(config=None):
    config=config or load_settings()
    validate_fiscal_settings(config)
    return create_nfce(config) if config.get("fiscal_type")=="NFC-e" else create_sat(config)
