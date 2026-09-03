from decimal import Decimal
from domain import Cart,Product
from nfce import focus_payload


def test_focus_payload_has_tax_and_customer():
    product=Product(1,"7891234567895","Produto",Decimal("100"),Decimal("2"),"12345678","5102","UN","0","00",Decimal("18"),"01",Decimal("0.65"),"01",Decimal("3"),"")
    cart=Cart(); cart.add(product); cart.set_discount("10",20)
    payload=focus_payload(cart,"PIX","52998224725",{"cnpj":"04.252.011/0001-10","tax_regime":"3"})
    assert payload["cpf_destinatario"]=="52998224725"
    assert payload["formas_pagamento"][0]["forma_pagamento"]=="17"
    assert payload["items"][0]["icms_situacao_tributaria"]=="00"
    assert payload["items"][0]["valor_desconto"]==10.0

def test_focus_payload_rejects_incomplete_tax_registration():
    cart=Cart(); cart.add(Product(1,"1","Sem fiscal",Decimal("10"),Decimal("1")))
    try: focus_payload(cart,"Dinheiro","",{"cnpj":"1","tax_regime":"3"})
    except ValueError as exc: assert "Cadastro fiscal incompleto" in str(exc)
    else: raise AssertionError("Produto sem tributação deveria ser bloqueado")
