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
    cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    min_stock: Mapped[Decimal] = mapped_column(Numeric(12, 3), default=0)
    category: Mapped[str] = mapped_column(String(60), default="Geral")
    origin: Mapped[str] = mapped_column(String(2), default="")
    icms_cst: Mapped[str] = mapped_column(String(4), default="")
    icms_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)
    pis_cst: Mapped[str] = mapped_column(String(3), default="")
    pis_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)
    cofins_cst: Mapped[str] = mapped_column(String(3), default="")
    cofins_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)
    cest: Mapped[str] = mapped_column(String(7), default="")
    ibscbs_cst: Mapped[str] = mapped_column(String(3), default="")
    tax_classification: Mapped[str] = mapped_column(String(6), default="")
    ibs_state_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)
    ibs_city_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)
    cbs_rate: Mapped[Decimal] = mapped_column(Numeric(7,4), default=0)

class SaleRow(Base):
    __tablename__ = "sales"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    subtotal: Mapped[Decimal] = mapped_column(Numeric(12,2))
    discount: Mapped[Decimal] = mapped_column(Numeric(12,2))
    total: Mapped[Decimal] = mapped_column(Numeric(12,2))
    payment: Mapped[str] = mapped_column(String(30))
    fiscal_key: Mapped[str] = mapped_column(String(80), default="")
    customer_document: Mapped[str] = mapped_column(String(14), default="")
    operator: Mapped[str] = mapped_column(String(60), default="ADMIN")
    cash_register: Mapped[str] = mapped_column(String(30), default="CAIXA 1")
    fiscal_type: Mapped[str] = mapped_column(String(10), default="")
    fiscal_status: Mapped[str] = mapped_column(String(20), default="AUTORIZADO")
    status: Mapped[str] = mapped_column(String(20), default="CONCLUIDA")

class StockMovementRow(Base):
    __tablename__ = "stock_movements"
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[object] = mapped_column(DateTime, server_default=func.now())
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    movement_type: Mapped[str] = mapped_column(String(20))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12,3))
    sale_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    operator: Mapped[str] = mapped_column(String(60), default="ADMIN")
    reason: Mapped[str] = mapped_column(String(140), default="")

class SaleItemRow(Base):
    __tablename__ = "sale_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    sale_id: Mapped[int] = mapped_column(ForeignKey("sales.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    description: Mapped[str] = mapped_column(String(140))
    quantity: Mapped[Decimal] = mapped_column(Numeric(12,3))
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12,2))
    total: Mapped[Decimal] = mapped_column(Numeric(12,2))

class NfceSequenceRow(Base):
    __tablename__ = "nfce_sequences"
    series: Mapped[int] = mapped_column(primary_key=True)
    last_number: Mapped[int] = mapped_column(Integer, default=0)

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
        if "cost" not in columns: conn.execute(text("ALTER TABLE products ADD COLUMN cost NUMERIC(12,2) DEFAULT 0"))
        if "min_stock" not in columns: conn.execute(text("ALTER TABLE products ADD COLUMN min_stock NUMERIC(12,3) DEFAULT 0"))
        if "category" not in columns: conn.execute(text("ALTER TABLE products ADD COLUMN category VARCHAR(60) DEFAULT 'Geral'"))
        for name,definition in (("origin","VARCHAR(2) DEFAULT ''"),("icms_cst","VARCHAR(4) DEFAULT ''"),("icms_rate","NUMERIC(7,4) DEFAULT 0"),("pis_cst","VARCHAR(3) DEFAULT ''"),("pis_rate","NUMERIC(7,4) DEFAULT 0"),("cofins_cst","VARCHAR(3) DEFAULT ''"),("cofins_rate","NUMERIC(7,4) DEFAULT 0"),("cest","VARCHAR(7) DEFAULT ''")):
            if name not in columns: conn.execute(text(f"ALTER TABLE products ADD COLUMN {name} {definition}"))
        for name,definition in (("ibscbs_cst","VARCHAR(3) DEFAULT ''"),("tax_classification","VARCHAR(6) DEFAULT ''"),("ibs_state_rate","NUMERIC(7,4) DEFAULT 0"),("ibs_city_rate","NUMERIC(7,4) DEFAULT 0"),("cbs_rate","NUMERIC(7,4) DEFAULT 0")):
            if name not in columns: conn.execute(text(f"ALTER TABLE products ADD COLUMN {name} {definition}"))
        sale_columns={row[1] for row in conn.execute(text("PRAGMA table_info(sales)"))}
        if "customer_document" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN customer_document VARCHAR(14) DEFAULT ''"))
        if "operator" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN operator VARCHAR(60) DEFAULT 'ADMIN'"))
        if "cash_register" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN cash_register VARCHAR(30) DEFAULT 'CAIXA 1'"))
        if "fiscal_type" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN fiscal_type VARCHAR(10) DEFAULT ''"))
        if "fiscal_status" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN fiscal_status VARCHAR(20) DEFAULT 'AUTORIZADO'"))
        if "status" not in sale_columns: conn.execute(text("ALTER TABLE sales ADD COLUMN status VARCHAR(20) DEFAULT 'CONCLUIDA'"))
    with Session.begin() as s:
        if not s.query(ProductRow).first():
            s.add_all([
                ProductRow(barcode="789100000001", name="Café Especial 500 g", price=32.90, stock=30, ncm="09012100"),
                ProductRow(barcode="789100000002", name="Água Mineral 500 ml", price=4.50, stock=80, ncm="22011000"),
                ProductRow(barcode="789100000003", name="Chocolate 90 g", price=8.90, stock=45, ncm="18063210"),
            ])

def to_product(row):
    return Product(row.id,row.barcode,row.name,row.price,row.stock,row.ncm,row.cfop,row.unit,row.origin,row.icms_cst,row.icms_rate,row.pis_cst,row.pis_rate,row.cofins_cst,row.cofins_rate,row.cest,row.ibscbs_cst,row.tax_classification,row.ibs_state_rate,row.ibs_city_rate,row.cbs_rate)

def find_product(term: str):
    with Session() as s:
        row = s.query(ProductRow).filter(ProductRow.active == 1, ProductRow.barcode == term.strip()).first()
        if not row:
            row = s.query(ProductRow).filter(ProductRow.active == 1, ProductRow.name.ilike(f"%{term.strip()}%" )).first()
        return to_product(row) if row else None

def persist_sale(cart, payment, fiscal_key, customer_document="", fiscal_type="", operator="ADMIN", cash_register="CAIXA 1"):
    with Session.begin() as s:
        sale = SaleRow(subtotal=cart.subtotal, discount=cart.discount, total=cart.total,
                       payment=payment, fiscal_key=fiscal_key, customer_document=customer_document,
                       fiscal_type=fiscal_type, operator=operator, cash_register=cash_register,
                       fiscal_status="AUTORIZADO", status="CONCLUIDA")
        s.add(sale); s.flush()
        for item in cart.items:
            row = s.get(ProductRow, item.product.id)
            if row.stock < item.quantity:
                raise ValueError(f"Estoque insuficiente: {row.name}")
            row.stock -= item.quantity
            s.add(SaleItemRow(sale_id=sale.id, product_id=row.id, description=row.name,
                              quantity=item.quantity, unit_price=row.price, total=item.total))
            s.add(StockMovementRow(product_id=row.id, movement_type="SAIDA", quantity=-item.quantity,
                                   sale_id=sale.id, operator=operator, reason="Venda concluída"))
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
        old_stock = Decimal(str(row.stock or 0)) if product_id else Decimal("0")
        for key in ("barcode","name","price","stock","ncm","cfop","unit","active","cost","min_stock","category","origin","icms_cst","icms_rate","pis_cst","pis_rate","cofins_cst","cofins_rate","cest","ibscbs_cst","tax_classification","ibs_state_rate","ibs_city_rate","cbs_rate"):
            setattr(row,key,data[key])
        s.add(row)
        s.flush()
        delta=Decimal(str(row.stock or 0))-old_stock
        if delta:
            s.add(StockMovementRow(product_id=row.id, movement_type="ENTRADA" if delta > 0 else "AJUSTE",
                                   quantity=delta, operator="ADMIN", reason="Cadastro/ajuste de produto"))

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

def reserve_nfce_number(series:int, configured_last:int=0):
    """Reserva um número dentro de transação SQLite; números não são reutilizados."""
    with Session.begin() as s:
        row=s.get(NfceSequenceRow,int(series))
        if row is None:
            row=NfceSequenceRow(series=int(series),last_number=int(configured_last)); s.add(row); s.flush()
        row.last_number=max(row.last_number,int(configured_last))+1
        return row.last_number
