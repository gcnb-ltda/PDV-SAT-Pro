from settings import validate_fiscal_settings, fiscal_fingerprint

def test_homologation_accepts_incomplete_configuration():
    assert validate_fiscal_settings({"environment":"homologacao","fiscal_type":"SAT"})

def test_direct_emission_requires_credential_and_matching_validation():
    values={"environment":"homologacao","fiscal_type":"NFC-e","uf":"SP",
            "nfce_direct_enabled":True,"sefaz_homologation_approved":True,
            "sefaz_credentialed":True,"cnpj":"12345678000195","ie":"1",
            "nfce_certificate":"cert.pfx","nfce_password":"secret","nfce_csc":"csc",
            "nfce_csc_id":"1","nfce_series":"1","street":"Rua A","address_number":"1",
            "district":"Centro","municipality_code":"3550308","municipality_name":"São Paulo",
            "nfce_qrcode_url":"https://example/q","nfce_consult_url":"https://example/c",
            "schema_dir":"schemas"}
    values["sefaz_validation_fingerprint"]=fiscal_fingerprint(values)
    assert validate_fiscal_settings(values)
    values["uf"]="RJ"
    try:
        validate_fiscal_settings(values)
    except ValueError as exc:
        assert "mudou" in str(exc)
    else:
        raise AssertionError("Alteração fiscal deveria exigir novo teste SEFAZ")

def test_production_rejects_missing_fiscal_data():
    try: validate_fiscal_settings({"environment":"producao","fiscal_type":"NFC-e"})
    except ValueError: pass
    else: raise AssertionError("Produção incompleta deveria ser recusada")
