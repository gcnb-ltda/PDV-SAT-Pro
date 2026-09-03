from datetime import datetime, timezone
from decimal import Decimal
import pytest
from domain import Cart, Product
from nfce_xml import NS, access_key, build_nfce, add_supplement
from sefaz_endpoints import endpoint, ibge_uf_code
from sefaz_soap import SefazSoapClient
from fiscal_storage import enqueue, pending

def config():
    return {"uf":"SP","cnpj":"12345678000195","ie":"123456789","company_name":"EMPRESA TESTE",
      "trade_name":"TESTE","street":"RUA TESTE","address_number":"1","district":"CENTRO","cep":"01001000",
      "municipality_code":"3550308","municipality_name":"SAO PAULO","environment":"homologacao",
      "tax_regime":"1","nfce_series":"1","nfce_last_number":"0","nfce_csc_id":"1","nfce_csc":"TOKEN",
      "nfce_qrcode_url":"https://example.test/qrcode","nfce_consult_url":"https://example.test/consulta"}

def cart():
    p=Product(1,"789100000001","PRODUTO TESTE",Decimal("10"),Decimal("5"),"09012100","5102","UN","0","102",Decimal("0"),"07",Decimal("0"),"07",Decimal("0"))
    c=Cart(); c.add(p,2); return c

def test_access_key_has_44_digits_and_valid_dv():
    key=access_key(config(),123,datetime(2026,9,3,tzinfo=timezone.utc),numeric_code="12345678")
    assert len(key)==44 and key.isdigit() and key.startswith("352609")

def test_nfce_400_has_required_groups_and_optional_customer():
    root,key,_=build_nfce(config(),cart(),"PIX","52998224725",issued=datetime(2026,9,3,tzinfo=timezone.utc))
    add_supplement(root,key,config()); ns={"n":NS}
    assert root.xpath("string(n:infNFe/@versao)",namespaces=ns)=="4.00"
    assert root.xpath("string(.//n:dest/n:CPF)",namespaces=ns)=="52998224725"
    assert root.xpath("string(.//n:det/n:prod/n:vProd)",namespaces=ns)=="20.00"
    assert "p="+key in root.xpath("string(.//n:qrCode)",namespaces=ns)

def test_sefaz_catalog_and_parser():
    assert ibge_uf_code("SP")=="35"; assert endpoint("RS","homologacao","status").startswith("https://")
    raw=b'<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope"><soap:Body><ret><cStat>107</cStat><xMotivo>Servico em Operacao</xMotivo></ret></soap:Body></soap:Envelope>'
    result=SefazSoapClient.parse(raw); assert result.status=="107"

def test_unknown_state_endpoint_fails_closed():
    with pytest.raises(RuntimeError): endpoint("MG","homologacao","status")

def test_offline_queue_is_atomic(tmp_path):
    path=enqueue("3526",b"<NFe/>",{"status":"PENDING"},tmp_path)
    assert path.read_bytes()==b"<NFe/>" and pending(tmp_path)==[path]
