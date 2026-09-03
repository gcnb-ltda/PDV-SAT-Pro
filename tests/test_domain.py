from decimal import Decimal
from domain import Cart, Product

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
