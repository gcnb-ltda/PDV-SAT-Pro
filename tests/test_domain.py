from decimal import Decimal
from domain import Cart, Product, customer_document

def test_cart_totals_and_discount():
    cart=Cart(); cart.add(Product(1,"1","Produto",Decimal("10.50"),Decimal("5")),2)
    cart.discount=Decimal("1.00")
    assert cart.subtotal == Decimal("21.00")
    assert cart.total == Decimal("20.00")

def test_same_product_is_merged():
    cart=Cart(); p=Product(1,"1","Produto",Decimal("2"),Decimal("5"))
    cart.add(p); cart.add(p,2)
    assert len(cart.items)==1 and cart.items[0].quantity==3

def test_quantity_cannot_exceed_stock():
    cart=Cart(); p=Product(1,"1","Produto",Decimal("2"),Decimal("2"))
    cart.add(p,2)
    try: cart.add(p)
    except ValueError: pass
    else: raise AssertionError("Venda acima do estoque deveria falhar")

def test_discount_limit():
    cart=Cart(); cart.add(Product(1,"1","Produto",Decimal("100"),Decimal("5")))
    cart.set_discount("20",20)
    assert cart.total == Decimal("80.00")
    try: cart.set_discount("20.01",20)
    except ValueError: pass
    else: raise AssertionError("Desconto acima do limite deveria falhar")

def test_optional_customer_document():
    assert customer_document("") == ""
    assert customer_document("529.982.247-25") == "52998224725"
    assert customer_document("04.252.011/0001-10") == "04252011000110"

def test_invalid_customer_document():
    for value in ("123", "111.111.111-11", "00.000.000/0000-00"):
        try: customer_document(value)
        except ValueError: pass
        else: raise AssertionError("CPF/CNPJ inválido deveria ser rejeitado")
