from __future__ import annotations

from datetime import date, timedelta

from qt_compat import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QLineEdit,QPushButton,
    QTableWidget,QTableWidgetItem,QHeaderView,QLabel,QFileDialog,QMessageBox,QDateEdit,QDate,
    QTabWidget,QWidget,dialog_exec)
from reports import REPORTS, generate_report, export_report
from audit import logger


def _python_date(widget):
    value=widget.date()
    return date(value.year(),value.month(),value.day())


class ReportsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Central de relatórios"); self.resize(1180,680)
        root=QVBoxLayout(self); filters=QHBoxLayout()
        self.kind=QComboBox()
        for key,title in REPORTS.items(): self.kind.addItem(title,key)
        today=date.today(); self.start=QDateEdit(QDate(today.year,today.month,1)); self.end=QDateEdit(QDate.currentDate())
        self.start.setCalendarPopup(True); self.end.setCalendarPopup(True)
        self.search=QLineEdit(); self.search.setPlaceholderText("Produto, código ou termo")
        self.payment=QComboBox(); self.payment.addItems(["Todos","PIX","Cartão de débito","Cartão de crédito","Dinheiro"])
        generate=QPushButton("Gerar relatório"); generate.setObjectName("primary"); generate.clicked.connect(self.generate)
        for label,widget in (("Relatório",self.kind),("Início",self.start),("Fim",self.end),("Busca",self.search),("Pagamento",self.payment)):
            box=QVBoxLayout(); box.addWidget(QLabel(label)); box.addWidget(widget); filters.addLayout(box)
        filters.addWidget(generate); root.addLayout(filters)
        self.summary=QLabel("Selecione um relatório e clique em Gerar relatório."); root.addWidget(self.summary)
        self.table=QTableWidget(); self.table.setSortingEnabled(True); self.table.setAlternatingRowColors(True); root.addWidget(self.table)
        actions=QHBoxLayout(); actions.addStretch()
        for label,ext in (("Exportar CSV","csv"),("Exportar XLSX","xlsx"),("Exportar PDF / Imprimir","pdf")):
            button=QPushButton(label); button.clicked.connect(lambda _,e=ext:self.export(e)); actions.addWidget(button)
        root.addLayout(actions); self.current=None; self.generate()

    def generate(self):
        try:
            start,end=_python_date(self.start),_python_date(self.end)
            if start>end: raise ValueError("A data inicial não pode ser posterior à data final.")
            self.current=generate_report(self.kind.currentData(),start,end,self.search.text(),self.payment.currentText())
            self.table.setSortingEnabled(False); self.table.clear(); self.table.setColumnCount(len(self.current.columns)); self.table.setHorizontalHeaderLabels(self.current.columns); self.table.setRowCount(len(self.current.rows))
            for row,values in enumerate(self.current.rows):
                for col,value in enumerate(values): self.table.setItem(row,col,QTableWidgetItem("" if value is None else str(value)))
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            if self.current.columns: self.table.horizontalHeader().setSectionResizeMode(min(1,len(self.current.columns)-1),QHeaderView.Stretch)
            self.table.setSortingEnabled(True); self.summary.setText(f"{self.current.title}  •  {self.current.summary}  •  {self.current.filters}")
            logger.info("Relatório gerado: %s",self.current.title)
        except Exception as exc: QMessageBox.critical(self,"Relatórios",str(exc))

    def export(self,extension):
        if not self.current: return
        safe="".join(c if c.isalnum() else "-" for c in self.current.title).strip("-").lower()
        filename=QFileDialog.getSaveFileName(self,"Exportar relatório",f"{safe}.{extension}",f"{extension.upper()} (*.{extension})")[0]
        if filename:
            if not filename.lower().endswith("."+extension): filename += "."+extension
            try:
                path=export_report(self.current,filename); logger.info("Relatório exportado: %s",path.name)
                QMessageBox.information(self,"Relatórios",f"Arquivo criado em:\n{path}")
            except Exception as exc: QMessageBox.critical(self,"Exportação",str(exc))


class DashboardDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Painel gerencial"); self.resize(900,600)
        root=QVBoxLayout(self); today=date.today(); start=today-timedelta(days=29)
        daily=generate_report("daily",start,today); top=generate_report("top_products",start,today)
        total=sum(float(str(row[2]).replace("R$ ","").replace(".","").replace(",",".")) for row in daily.rows) if daily.rows else 0
        sales=sum(int(row[1]) for row in daily.rows); ticket=total/sales if sales else 0
        cards=QHBoxLayout()
        for title,value in (("Faturamento — 30 dias",f"R$ {total:,.2f}"),("Vendas",str(sales)),("Ticket médio",f"R$ {ticket:,.2f}"),("Produtos vendidos",str(len(top.rows)))):
            label=QLabel(f"{title}\n{value}".replace(",","X").replace(".",",").replace("X",".")); label.setStyleSheet("background:#171d28;border-radius:12px;padding:18px;font-size:18px;font-weight:700;color:#f3c623"); cards.addWidget(label)
        root.addLayout(cards); root.addWidget(QLabel("Produtos mais vendidos nos últimos 30 dias"))
        table=QTableWidget(min(10,len(top.rows)),len(top.columns)); table.setHorizontalHeaderLabels(top.columns)
        for r,row in enumerate(top.rows[:10]):
            for c,value in enumerate(row): table.setItem(r,c,QTableWidgetItem(str(value)))
        table.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch); root.addWidget(table)
