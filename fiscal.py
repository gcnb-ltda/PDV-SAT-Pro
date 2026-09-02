from settings import load_settings
from sat import create_sat
from nfce import create_nfce

def create_fiscal(config=None):
    config=config or load_settings()
    return create_nfce(config) if config.get("fiscal_type")=="NFC-e" else create_sat(config)

