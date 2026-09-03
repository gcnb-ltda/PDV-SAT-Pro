from __future__ import annotations
from decimal import Decimal
from qt_compat import (Qt,QKeySequence,QShortcut,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,QLabel,
    QLineEdit,QPushButton,QTableWidget,QTableWidgetItem,QHeaderView,QMessageBox,QComboBox,QInputDialog,
    QFrame,dialog_exec)
from domain import Cart, money
from database import find_product, persist_sale, check_stock
from config_dialog import FiscalConfigDialog
from fiscal import create_fiscal
from dialogs import ProductsDialog,SalesHistoryDialog,BackupDialog
from settings import load_settings
from audit import logger

STYLE = """
QWidget{background:#0b0e13;color:#eef2f7;font:14px 'Segoe UI'}
QFrame#side{background:#121722;border:1px solid #222a38;border-radius:16px}
QLineEdit,QComboBox{background:#171d28;border:1px solid #2b3445;border-radius:10px;padding:12px}
QLineEdit:focus{border:1px solid #f3c623}
QPushButton{background:#202838;border:0;border-radius:10px;padding:12px;font-weight:600}
QPushButton:hover{background:#2a354a} QPushButton#primary{background:#f3c623;color:#121212}
QTableWidget{background:#111620;border:0;gridline-color:#273043;border-radius:12px}
QHeaderView::section{background:#171d28;color:#9ca8ba;border:0;padding:10px}
QLabel#brand{font-size:25px;font-weight:800;color:#f3c623} QLabel#total{font-size:42px;font-weight:800;color:#f3c623}
"""

class MainWindow(QMainWindow):
    def __init__(self, sat):
        super().__init__(); self.sat=sat; self.cart=Cart()
        self.setWindowTitle("PDV SAT Pro"); self.resize(1180, 720); self.setStyleSheet(STYLE)
        root=QWidget(); self.setCentralWidget(root); layout=QHBoxLayout(root); layout.setContentsMargins(22,22,22,22); layout.setSpacing(18)
        left=QVBoxLayout(); brand=QLabel("PDV  /  SAT PRO"); brand.setObjectName("brand"); left.addWidget(brand)
        self.search=QLineEdit(); self.search.setPlaceholderText("Código de barras ou nome do produto  •  F2"); self.search.returnPressed.connect(self.add_product); left.addWidget(self.search)
        self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["Produto","Qtd.","Unitário","Total",""])
        self.table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch); self.table.setSelectionBehavior(QTableWidget.SelectRows); self.table.doubleClicked.connect(self.edit_quantity); left.addWidget(self.table)
        footer=QHBoxLayout(); hint=QLabel("F2 Buscar   •   F4 Finalizar   •   F8 Cancelar venda"); hint.setStyleSheet("color:#7f8ba0")
        products=QPushButton("Produtos"); history=QPushButton("Histórico"); backup=QPushButton("Backup"); settings=QPushButton("Configuração fiscal")
        products.clicked.connect(lambda:dialog_exec(ProductsDialog(self))); history.clicked.connect(lambda:dialog_exec(SalesHistoryDialog(self))); backup.clicked.connect(lambda:dialog_exec(BackupDialog(self))); settings.clicked.connect(self.open_settings)
        footer.addWidget(hint); footer.addStretch(); footer.addWidget(products); footer.addWidget(history); footer.addWidget(backup); footer.addWidget(settings); left.addLayout(footer); layout.addLayout(left,3)
        side=QFrame(); side.setObjectName("side"); sv=QVBoxLayout(side); sv.setContentsMargins(24,24,24,24)
        sv.addWidget(QLabel("RESUMO DA VENDA")); self.count=QLabel("0 itens"); sv.addWidget(self.count); sv.addStretch()
        sv.addWidget(QLabel("TOTAL")); self.total=QLabel("R$ 0,00"); self.total.setObjectName("total"); sv.addWidget(self.total)
        self.payment=QComboBox(); self.payment.addItems(["PIX","Cartão de débito","Cartão de crédito","Dinheiro"]); self.payment.currentTextChanged.connect(self.payment_changed); sv.addWidget(self.payment)
        self.received=QLineEdit(); self.received.setPlaceholderText("Valor recebido em dinheiro"); self.received.setVisible(False); self.received.textChanged.connect(self.refresh_change); sv.addWidget(self.received)
        self.change=QLabel(""); sv.addWidget(self.change)
        discount=QPushButton("Aplicar desconto"); discount.clicked.connect(self.apply_discount); sv.addWidget(discount)
        finish=QPushButton("Finalizar venda  F4"); finish.setObjectName("primary"); finish.clicked.connect(self.finish); sv.addWidget(finish)
        self.fiscal_status=QLabel(self.sat.status()); self.fiscal_status.setWordWrap(True); self.fiscal_status.setStyleSheet("color:#7ee2a8;margin-top:10px"); sv.addWidget(self.fiscal_status); layout.addWidget(side,1)
        QShortcut(QKeySequence("F2"),self,self.search.setFocus); QShortcut(QKeySequence("F4"),self,self.finish); QShortcut(QKeySequence("F8"),self,self.cancel)
        self.search.setFocus()

    def add_product(self):
        try:
            p=find_product(self.search.text())
            if not p: QMessageBox.warning(self,"Produto","Produto não encontrado."); return
            self.cart.add(p); self.search.clear(); self.refresh()
        except Exception as exc: QMessageBox.warning(self,"Produto",str(exc))

    def open_settings(self):
        if dialog_exec(FiscalConfigDialog(self)):
            self.sat=create_fiscal(); self.fiscal_status.setText(self.sat.status())

    def refresh(self):
        self.table.setRowCount(0)
        for index,item in enumerate(self.cart.items):
            row=self.table.rowCount(); self.table.insertRow(row)
            values=[item.product.name,str(item.quantity),f"R$ {item.product.price:.2f}",f"R$ {item.total:.2f}"]
            for col,value in enumerate(values): self.table.setItem(row,col,QTableWidgetItem(value))
            remove=QPushButton("Remover"); remove.clicked.connect(lambda _,i=index:self.remove(i)); self.table.setCellWidget(row,4,remove)
        qty=sum((i.quantity for i in self.cart.items),Decimal("0")); self.count.setText(f"{qty} item(ns)")
        self.total.setText("R$ "+f"{self.cart.total:,.2f}".replace(",","X").replace(".",",").replace("X","."))
        self.refresh_change()

    def remove(self,index): self.cart.items.pop(index); self.refresh()
    def edit_quantity(self,*_):
        row=self.table.currentRow()
        if row >= 0:
            value,ok=QInputDialog.getDouble(self,"Quantidade","Nova quantidade:",float(self.cart.items[row].quantity),0.001,999999,3)
            if ok:
                try: self.cart.set_quantity(row,value); self.refresh()
                except Exception as exc: QMessageBox.warning(self,"Quantidade",str(exc))
    def apply_discount(self):
        config=load_settings(); maximum=Decimal(str(config.get("max_discount_percent","20")))
        value,ok=QInputDialog.getDouble(self,"Desconto",f"Valor do desconto (limite {maximum}%):",float(self.cart.discount),0,float(self.cart.subtotal),2)
        if ok:
            try: self.cart.set_discount(value,maximum); self.refresh()
            except Exception as exc: QMessageBox.warning(self,"Desconto",str(exc))
    def payment_changed(self,value):
        self.received.setVisible(value=="Dinheiro"); self.refresh_change()
    def refresh_change(self):
        if self.payment.currentText() != "Dinheiro": self.change.setText(""); return
        try:
            received=money((self.received.text() or "0").replace(",",".")); change=received-self.cart.total
            self.change.setText(f"Troco: R$ {max(change,Decimal('0')):.2f}")
        except Exception: self.change.setText("Informe um valor válido")
    def cancel(self):
        if self.cart.items and QMessageBox.question(self,"Cancelar","Cancelar a venda atual?")==QMessageBox.Yes: self.cart=Cart(); self.refresh()
    def finish(self):
        if not self.cart.items: QMessageBox.information(self,"Venda","Adicione produtos ao carrinho."); return
        try:
            check_stock(self.cart)
            if self.payment.currentText()=="Dinheiro":
                received=money((self.received.text() or "0").replace(",","."))
                if received < self.cart.total: raise ValueError("Valor recebido é menor que o total da venda.")
            result=self.sat.authorize(self.cart,self.payment.currentText())
            if not result.success: raise RuntimeError("Emissor fiscal recusou a venda: "+result.raw)
            sale_id=persist_sale(self.cart,self.payment.currentText(),result.key)
            logger.info("Venda %s concluída; emissor=%s",sale_id,type(self.sat).__name__)
            QMessageBox.information(self,"Venda concluída",f"Venda #{sale_id} autorizada.\nChave: {result.key}")
            self.cart=Cart(); self.received.clear(); self.refresh(); self.search.setFocus()
        except Exception as exc: logger.exception("Falha operacional na finalização"); QMessageBox.critical(self,"Falha ao finalizar",str(exc))
