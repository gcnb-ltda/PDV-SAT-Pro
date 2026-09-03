from decimal import Decimal
from qt_compat import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLineEdit,QPushButton,QTableWidget,
    QTableWidgetItem,QHeaderView,QMessageBox,QComboBox,QCheckBox,QDoubleSpinBox,QLabel,QFileDialog,
    dialog_exec)
from database import list_products,save_product,list_sales
from backup import create_backup,restore_backup

class ProductEditDialog(QDialog):
    def __init__(self,row=None,parent=None):
        super().__init__(parent); self.row=row; self.setWindowTitle("Produto"); form=QFormLayout(self)
        def field(value=""): return QLineEdit(str(value or ""))
        self.barcode=field(getattr(row,"barcode","")); self.name=field(getattr(row,"name",""))
        self.price=QDoubleSpinBox(); self.price.setMaximum(9_999_999); self.price.setDecimals(2); self.price.setValue(float(getattr(row,"price",0)))
        self.stock=QDoubleSpinBox(); self.stock.setMaximum(9_999_999); self.stock.setDecimals(3); self.stock.setValue(float(getattr(row,"stock",0)))
        self.unit=field(getattr(row,"unit","UN")); self.ncm=field(getattr(row,"ncm","")); self.cfop=field(getattr(row,"cfop","5102")); self.active=QCheckBox(); self.active.setChecked(bool(getattr(row,"active",1)))
        for label,widget in (("Código de barras",self.barcode),("Descrição",self.name),("Preço",self.price),("Estoque",self.stock),("Unidade",self.unit),("NCM",self.ncm),("CFOP",self.cfop),("Ativo",self.active)): form.addRow(label,widget)
        save=QPushButton("Salvar"); save.setObjectName("primary"); save.clicked.connect(self.persist); form.addRow(save)
    def persist(self):
        if not self.barcode.text().strip() or not self.name.text().strip(): QMessageBox.warning(self,"Produto","Código e descrição são obrigatórios."); return
        if len(self.ncm.text().strip()) not in (0,8): QMessageBox.warning(self,"Produto","NCM deve possuir 8 dígitos."); return
        data={"barcode":self.barcode.text().strip(),"name":self.name.text().strip(),"price":Decimal(str(self.price.value())),"stock":Decimal(str(self.stock.value())),"unit":self.unit.text().strip().upper() or "UN","ncm":self.ncm.text().strip(),"cfop":self.cfop.text().strip() or "5102","active":1 if self.active.isChecked() else 0}
        try: save_product(data,getattr(self.row,"id",None)); self.accept()
        except Exception as exc: QMessageBox.critical(self,"Produto",str(exc))

class ProductsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Cadastro de produtos"); self.resize(900,560); root=QVBoxLayout(self)
        bar=QHBoxLayout(); new=QPushButton("Novo produto"); edit=QPushButton("Editar selecionado"); new.clicked.connect(self.new); edit.clicked.connect(self.edit); bar.addWidget(new); bar.addWidget(edit); bar.addStretch(); root.addLayout(bar)
        self.table=QTableWidget(0,8); self.table.setHorizontalHeaderLabels(["ID","Código","Descrição","Preço","Estoque","Un.","NCM","Status"]); self.table.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch); self.table.doubleClicked.connect(self.edit); root.addWidget(self.table); self.reload()
    def reload(self):
        self.rows=list_products(); self.table.setRowCount(0)
        for p in self.rows:
            row=self.table.rowCount(); self.table.insertRow(row)
            for col,value in enumerate((p.id,p.barcode,p.name,f"R$ {p.price:.2f}",p.stock,p.unit,p.ncm,"Ativo" if p.active else "Inativo")): self.table.setItem(row,col,QTableWidgetItem(str(value)))
    def new(self):
        if dialog_exec(ProductEditDialog(parent=self)): self.reload()
    def edit(self,*_):
        row=self.table.currentRow()
        if row < 0: QMessageBox.information(self,"Produtos","Selecione um produto."); return
        if dialog_exec(ProductEditDialog(self.rows[row],self)): self.reload()

class SalesHistoryDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Histórico de vendas"); self.resize(900,520); root=QVBoxLayout(self)
        self.table=QTableWidget(0,7); self.table.setHorizontalHeaderLabels(["Venda","Data","Subtotal","Desconto","Total","Pagamento","Documento fiscal"]); self.table.horizontalHeader().setSectionResizeMode(6,QHeaderView.Stretch); root.addWidget(self.table)
        for sale in list_sales():
            row=self.table.rowCount(); self.table.insertRow(row)
            for col,value in enumerate((sale.id,sale.created_at,f"R$ {sale.subtotal:.2f}",f"R$ {sale.discount:.2f}",f"R$ {sale.total:.2f}",sale.payment,sale.fiscal_key)): self.table.setItem(row,col,QTableWidgetItem(str(value)))

class BackupDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Backup e restauração"); root=QVBoxLayout(self); root.addWidget(QLabel("Crie cópias periódicas. A restauração mantém uma cópia de segurança do banco atual."))
        backup=QPushButton("Criar backup"); restore=QPushButton("Restaurar backup"); backup.clicked.connect(self.backup); restore.clicked.connect(self.restore); root.addWidget(backup); root.addWidget(restore)
    def backup(self):
        folder=QFileDialog.getExistingDirectory(self,"Destino do backup")
        if folder:
            try: QMessageBox.information(self,"Backup",f"Backup criado em:\n{create_backup(folder)}")
            except Exception as exc: QMessageBox.critical(self,"Backup",str(exc))
    def restore(self):
        file=QFileDialog.getOpenFileName(self,"Selecionar backup",filter="Banco SQLite (*.db)")[0]
        if file and QMessageBox.question(self,"Restaurar","Substituir o banco atual e reiniciar o sistema?")==QMessageBox.Yes:
            try: safety=restore_backup(file); QMessageBox.information(self,"Restauração",f"Banco restaurado. Reinicie o PDV.\nCópia anterior: {safety}"); self.accept()
            except Exception as exc: QMessageBox.critical(self,"Restauração",str(exc))
