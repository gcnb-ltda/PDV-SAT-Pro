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

