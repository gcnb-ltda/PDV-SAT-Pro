from __future__ import annotations
import os
from pathlib import Path
from platformdirs import user_data_dir
from decimal import Decimal
from sqlalchemy import create_engine, String, Numeric, Integer, DateTime, ForeignKey, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.sql import func
from domain import Product

class Base(DeclarativeBase): pass

class ProductRow(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True)
    barcode: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(140), index=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    ncm: Mapped[str] = mapped_column(String(8), default="")
    cfop: Mapped[str] = mapped_column(String(4), default="5102")
    unit: Mapped[str] = mapped_column(String(8), default="UN")
    active: Mapped[int] = mapped_column(Integer, default=1)

class SaleRow(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2))
    discount: Mapped[Decimal] = mapped_column(Numeric(12,2))
    total: Mapped[Decimal] = mapped_column(Numeric(12,2))
    payment: Mapped[str] = mapped_column(String(30))
    fiscal_key: Mapped[str] = mapped_column(String(80), default="")

class SaleItemRow(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    description: Mapped[str] = mapped_column(String(140))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12,3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12,2))
    total: Mapped[Decimal] = mapped_column(Numeric(12,2))

DATA_DIR = Path(user_data_dir("PDV-SAT-Pro", "GCNB"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "pdv.db"
engine = create_engine(os.getenv("PDV_DB_URL", f"sqlite:///{DB_FILE}"))
Session = sessionmaker(engine, expire_on_commit=False)

def init_db():
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        columns={row[1] for row in conn.execute(text("PRAGMA table_info(products)"))}
        if "unit" not in columns: conn.execute(text("ALTER TABLE products ADD COLUMN unit VARCHAR(8) DEFAULT 'UN'"))
        if "active" not in columns: conn.execute(text("ALTER TABLE products ADD COLUMN active INTEGER DEFAULT 1"))
    with Session.begin() as s:
        if not s.query(ProductRow).first():
            s.add_all([
                ProductRow(barcode="789100000001", name="Café Especial 500 g", price=32.90, stock=30, ncm="09012100"),
                ProductRow(barcode="789100000002", name="Água Mineral 500 ml", price=4.50, stock=80, ncm="22011000"),
                ProductRow(barcode="789100000003", name="Chocolate 90 g", price=8.90, stock=45, ncm="18063210"),
            ])

def to_product(row):
    return Product(row.id, row.barcode, row.name, row.price, row.stock, row.ncm, row.cfop)

def find_product(term: str):
    with Session() as s:
        row = s.query(ProductRow).filter(ProductRow.active == 1, ProductRow.barcode == term.strip()).first()
        if not row:
            row = s.query(ProductRow).filter(ProductRow.active == 1, ProductRow.name.ilike(f"%{term.strip()}%" )).first()
        return to_product(row) if row else None

def persist_sale(cart, payment, fiscal_key):
    with Session.begin() as s:
        sale = SaleRow(subtotal=cart.subtotal, discount=cart.discount, total=cart.total,
                       payment=payment, fiscal_key=fiscal_key)
        s.add(sale); s.flush()
        for item in cart.items:
            row = s.get(ProductRow, item.product.id)
            if row.stock < item.quantity:
                raise ValueError(f"Estoque insuficiente: {row.name}")
            row.stock -= item.quantity
            s.add(SaleItemRow(sale_id=sale.id, product_id=row.id, description=row.name,
                              quantity=item.quantity, unit_price=row.price, total=item.total))
        return sale.id

def list_products(include_inactive=True):
    with Session() as s:
        query=s.query(ProductRow)
        if not include_inactive: query=query.filter(ProductRow.active == 1)
        return query.order_by(ProductRow.name).all()

def save_product(data, product_id=None):
    with Session.begin() as s:
        row=s.get(ProductRow, product_id) if product_id else ProductRow()
        if not row: raise ValueError("Produto não encontrado.")
        duplicate=s.query(ProductRow).filter(ProductRow.barcode == data["barcode"])
        if product_id: duplicate=duplicate.filter(ProductRow.id != product_id)
        if duplicate.first(): raise ValueError("Código de barras já cadastrado.")
        for key in ("barcode","name","price","stock","ncm","cfop","unit","active"):
            setattr(row,key,data[key])
        s.add(row)

def list_sales(limit=500):
    with Session() as s:
        return s.query(SaleRow).order_by(SaleRow.id.desc()).limit(limit).all()

def check_stock(cart):
    with Session() as s:
        for item in cart.items:
            row=s.get(ProductRow,item.product.id)
            if not row or not row.active or row.stock < item.quantity:
                raise ValueError(f"Estoque indisponível: {item.product.name}")

def database_file(): return DB_FILE
