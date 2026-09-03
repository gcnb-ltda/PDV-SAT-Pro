from settings import validate_fiscal_settings

def test_homologation_accepts_incomplete_configuration():
    assert validate_fiscal_settings({"environment":"homologacao","fiscal_type":"SAT"})

def test_production_rejects_missing_fiscal_data():
    try: validate_fiscal_settings({"environment":"producao","fiscal_type":"NFC-e"})
    except ValueError: pass
    else: raise AssertionError("Produção incompleta deveria ser recusada")
