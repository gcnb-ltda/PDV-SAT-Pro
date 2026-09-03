from __future__ import annotations
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

MONEY = Decimal("0.01")

def only_digits(value) -> str:
    return "".join(char for char in str(value or "") if char.isdigit())

def _valid_check_digits(number: str, weights: list[int]) -> bool:
    total = sum(int(digit) * weight for digit, weight in zip(number, weights))
    digit = 11 - total % 11
    return int(number[len(weights)]) == (0 if digit >= 10 else digit)

def customer_document(value) -> str:
    """Normaliza e valida CPF/CNPJ opcional informado para o documento fiscal."""
    number = only_digits(value)
    if not number:
        return ""
    if len(number) == 11:
        valid = len(set(number)) > 1 and _valid_check_digits(number, list(range(10, 1, -1))) \
            and _valid_check_digits(number, list(range(11, 1, -1)))
    elif len(number) == 14:
        valid = len(set(number)) > 1 and _valid_check_digits(number, [5,4,3,2,9,8,7,6,5,4,3,2]) \
            and _valid_check_digits(number, [6,5,4,3,2,9,8,7,6,5,4,3,2])
    else:
        valid = False
    if not valid:
        raise ValueError("CPF ou CNPJ do cliente é inválido.")
    return number

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
    unit: str = "UN"
    origin: str = ""
    icms_cst: str = ""
    icms_rate: Decimal = Decimal("0")
    pis_cst: str = ""
    pis_rate: Decimal = Decimal("0")
    cofins_cst: str = ""
    cofins_rate: Decimal = Decimal("0")
    cest: str = ""

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
        if qty <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        current = next((i for i in self.items if i.product.id == product.id), None)
        new_quantity = (current.quantity if current else Decimal("0")) + qty
        if new_quantity > product.stock:
            raise ValueError(f"Estoque insuficiente: {product.name}")
        if current:
            current.quantity += qty
        else:
            self.items.append(CartItem(product, qty))

    def set_quantity(self, index: int, quantity):
        qty = Decimal(str(quantity))
        if qty <= 0:
            raise ValueError("A quantidade deve ser maior que zero.")
        item = self.items[index]
        if qty > item.product.stock:
            raise ValueError(f"Estoque insuficiente: {item.product.name}")
        item.quantity = qty

    def set_discount(self, value, maximum_percent=Decimal("20")):
        discount = money(value)
        limit = money(self.subtotal * Decimal(str(maximum_percent)) / Decimal("100"))
        if discount < 0 or discount > limit:
            raise ValueError(f"Desconto máximo permitido: R$ {limit:.2f}")
        self.discount = discount

    @property
    def subtotal(self):
        return money(sum((i.total for i in self.items), Decimal("0")))

    @property
    def total(self):
        return max(Decimal("0"), money(self.subtotal - self.discount))
