from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

MONEY = Decimal("0.01")

def money(value) -> Decimal:
    return Decimal(str(value)).quantize(MONEY, rounding=ROUND_HALF_UP)

@dataclass(frozen=True)
class Product:
    id: int
    barcode: str
    name: str
    price: Decimal
    stock: Decimal
    ncm: str = ""
    cfop: str = "5102"

@dataclass
class CartItem:
    product: Product
    quantity: Decimal = Decimal("1")

    @property
    def total(self):
        return money(self.product.price * self.quantity)

@dataclass
class Cart:
    items: list[CartItem] = field(default_factory=list)
    discount: Decimal = Decimal("0")

    def add(self, product: Product, quantity=1):
        qty = Decimal(str(quantity))
        current = next((i for i in self.items if i.product.id == product.id), None)
        if current:
            current.quantity += qty
        else:
            self.items.append(CartItem(product, qty))

    @property
    def subtotal(self):
        return money(sum((i.total for i in self.items), Decimal("0")))

    @property
    def total(self):
        return max(Decimal("0"), money(self.subtotal - self.discount))

