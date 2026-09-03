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
        self.cost=QDoubleSpinBox(); self.cost.setMaximum(9_999_999); self.cost.setDecimals(2); self.cost.setValue(float(getattr(row,"cost",0)))
        self.min_stock=QDoubleSpinBox(); self.min_stock.setMaximum(9_999_999); self.min_stock.setDecimals(3); self.min_stock.setValue(float(getattr(row,"min_stock",0)))
        self.unit=field(getattr(row,"unit","UN")); self.category=field(getattr(row,"category","Geral")); self.ncm=field(getattr(row,"ncm","")); self.cfop=field(getattr(row,"cfop","5102")); self.origin=field(getattr(row,"origin","")); self.icms_cst=field(getattr(row,"icms_cst","")); self.icms_rate=field(getattr(row,"icms_rate","0")); self.pis_cst=field(getattr(row,"pis_cst","")); self.pis_rate=field(getattr(row,"pis_rate","0")); self.cofins_cst=field(getattr(row,"cofins_cst","")); self.cofins_rate=field(getattr(row,"cofins_rate","0")); self.cest=field(getattr(row,"cest","")); self.active=QCheckBox(); self.active.setChecked(bool(getattr(row,"active",1)))
        for label,widget in (("Código de barras",self.barcode),("Descrição",self.name),("Preço de venda",self.price),("Custo",self.cost),("Estoque",self.stock),("Estoque mínimo",self.min_stock),("Unidade",self.unit),("Categoria",self.category),("NCM",self.ncm),("CEST",self.cest),("CFOP",self.cfop),("Origem ICMS",self.origin),("CST/CSOSN ICMS",self.icms_cst),("Alíquota ICMS %",self.icms_rate),("CST PIS",self.pis_cst),("Alíquota PIS %",self.pis_rate),("CST COFINS",self.cofins_cst),("Alíquota COFINS %",self.cofins_rate),("Ativo",self.active)): form.addRow(label,widget)
        save=QPushButton("Salvar"); save.setObjectName("primary"); save.clicked.connect(self.persist); form.addRow(save)
    def persist(self):
        if not self.barcode.text().strip() or not self.name.text().strip(): QMessageBox.warning(self,"Produto","Código e descrição são obrigatórios."); return
        if len(self.ncm.text().strip()) not in (0,8): QMessageBox.warning(self,"Produto","NCM deve possuir 8 dígitos."); return
        try: rates={key:Decimal(widget.text().replace(",",".") or "0") for key,widget in (("icms_rate",self.icms_rate),("pis_rate",self.pis_rate),("cofins_rate",self.cofins_rate))}
        except Exception: QMessageBox.warning(self,"Produto","Alíquotas fiscais inválidas."); return
        data={"barcode":self.barcode.text().strip(),"name":self.name.text().strip(),"price":Decimal(str(self.price.value())),"cost":Decimal(str(self.cost.value())),"stock":Decimal(str(self.stock.value())),"min_stock":Decimal(str(self.min_stock.value())),"unit":self.unit.text().strip().upper() or "UN","category":self.category.text().strip() or "Geral","ncm":self.ncm.text().strip(),"cest":self.cest.text().strip(),"cfop":self.cfop.text().strip() or "5102","origin":self.origin.text().strip(),"icms_cst":self.icms_cst.text().strip(),"pis_cst":self.pis_cst.text().strip(),"cofins_cst":self.cofins_cst.text().strip(),"active":1 if self.active.isChecked() else 0}|rates
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
        self.table=QTableWidget(0,8); self.table.setHorizontalHeaderLabels(["Venda","Data","Subtotal","Desconto","Total","Pagamento","Cliente CPF/CNPJ","Documento fiscal"]); self.table.horizontalHeader().setSectionResizeMode(7,QHeaderView.Stretch); root.addWidget(self.table)
        for sale in list_sales():
            row=self.table.rowCount(); self.table.insertRow(row)
            for col,value in enumerate((sale.id,sale.created_at,f"R$ {sale.subtotal:.2f}",f"R$ {sale.discount:.2f}",f"R$ {sale.total:.2f}",sale.payment,sale.customer_document or "Consumidor não identificado",sale.fiscal_key)): self.table.setItem(row,col,QTableWidgetItem(str(value)))

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
