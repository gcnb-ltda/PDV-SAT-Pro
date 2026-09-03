from __future__ import annotations

from datetime import date, timedelta

from qt_compat import (QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QLineEdit,QPushButton,
    QTableWidget,QTableWidgetItem,QHeaderView,QLabel,QFileDialog,QMessageBox,QDateEdit,QDate,
    QTabWidget,QWidget,dialog_exec)
from reports import REPORTS, generate_report, export_report
from report_charts import ReportChart, chart_for
from report_scheduler import load_schedules,add_schedule,delete_schedule
from settings import load_settings
from audit import logger


def _python_date(widget):
    value=widget.date()
    return date(value.year(),value.month(),value.day())


class ReportsDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Central de relatórios"); self.resize(1180,680)
        root=QVBoxLayout(self); filters=QHBoxLayout()
        self.kind=QComboBox()
        role=load_settings().get("report_role","ADMIN")
        sensitive={"profitability","operators","fiscal_errors","taxes","audit"}
        for key,title in REPORTS.items():
            if role in ("ADMIN","GERENTE") or key not in sensitive: self.kind.addItem(title,key)
        today=date.today(); self.start=QDateEdit(QDate(today.year,today.month,1)); self.end=QDateEdit(QDate.currentDate())
        self.start.setCalendarPopup(True); self.end.setCalendarPopup(True)
        self.search=QLineEdit(); self.search.setPlaceholderText("Produto, código ou termo")
        self.payment=QComboBox(); self.payment.addItems(["Todos","PIX","Cartão de débito","Cartão de crédito","Dinheiro"])
        generate=QPushButton("Gerar relatório"); generate.setObjectName("primary"); generate.clicked.connect(self.generate)
        for label,widget in (("Relatório",self.kind),("Início",self.start),("Fim",self.end),("Busca",self.search),("Pagamento",self.payment)):
            box=QVBoxLayout(); box.addWidget(QLabel(label)); box.addWidget(widget); filters.addLayout(box)
        filters.addWidget(generate); root.addLayout(filters)
        self.summary=QLabel("Selecione um relatório e clique em Gerar relatório."); root.addWidget(self.summary)
        self.chart=ReportChart(); root.addWidget(self.chart)
        self.table=QTableWidget(); self.table.setSortingEnabled(True); self.table.setAlternatingRowColors(True); root.addWidget(self.table)
        self.page=0; self.page_size=100; pager=QHBoxLayout(); previous=QPushButton("Página anterior"); next_page=QPushButton("Próxima página"); self.page_label=QLabel(); previous.clicked.connect(lambda checked=False:self.change_page(-1)); next_page.clicked.connect(lambda checked=False:self.change_page(1)); pager.addWidget(previous); pager.addWidget(self.page_label); pager.addWidget(next_page); pager.addStretch(); root.addLayout(pager)
        actions=QHBoxLayout(); schedule=QPushButton("Agendar relatórios"); schedule.clicked.connect(lambda checked=False:dialog_exec(SchedulesDialog(self))); actions.addWidget(schedule); actions.addStretch()
        self.export_buttons={}
        for label,ext in (("Exportar CSV","csv"),("Exportar XLSX","xlsx"),("Exportar PDF / Imprimir","pdf")):
            button=QPushButton(label); button.setObjectName("export_"+ext); button.clicked.connect(lambda checked=False,e=ext:self.export(e)); actions.addWidget(button); self.export_buttons[ext]=button
        root.addLayout(actions); self.current=None; self.generate()

    def generate(self):
        try:
            start,end=_python_date(self.start),_python_date(self.end)
            if start>end: raise ValueError("A data inicial não pode ser posterior à data final.")
            self.current=generate_report(self.kind.currentData(),start,end,self.search.text(),self.payment.currentText())
            self.chart.set_data(chart_for(self.kind.currentData(),self.current))
            self.page=0; self.render_page()
            logger.info("Relatório gerado: %s",self.current.title)
        except Exception as exc: QMessageBox.critical(self,"Relatórios",str(exc))

    def render_page(self):
            rows=self.current.rows[self.page*self.page_size:(self.page+1)*self.page_size]
            self.table.setSortingEnabled(False); self.table.clear(); self.table.setColumnCount(len(self.current.columns)); self.table.setHorizontalHeaderLabels(self.current.columns); self.table.setRowCount(len(rows))
            for row,values in enumerate(rows):
                for col,value in enumerate(values): self.table.setItem(row,col,QTableWidgetItem("" if value is None else str(value)))
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
            if self.current.columns: self.table.horizontalHeader().setSectionResizeMode(min(1,len(self.current.columns)-1),QHeaderView.Stretch)
            self.table.setSortingEnabled(True); pages=max(1,(len(self.current.rows)+self.page_size-1)//self.page_size); self.page_label.setText(f"Página {self.page+1} de {pages}"); self.summary.setText(f"{self.current.title}  •  {self.current.summary}  •  {self.current.filters}")

    def change_page(self,direction):
        if not self.current: return
        pages=max(1,(len(self.current.rows)+self.page_size-1)//self.page_size); new=max(0,min(pages-1,self.page+direction))
        if new != self.page: self.page=new; self.render_page()

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


class SchedulesDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Agendamento de relatórios"); self.resize(760,440); root=QVBoxLayout(self)
        form=QHBoxLayout(); self.kind=QComboBox(); [self.kind.addItem(title,key) for key,title in REPORTS.items()]; self.frequency=QComboBox(); self.frequency.addItems(["Diário","Semanal","Mensal"]); self.format=QComboBox(); self.format.addItems(["xlsx","csv","pdf"]); self.folder=QLineEdit(); self.folder.setReadOnly(True); pick=QPushButton("Pasta"); pick.clicked.connect(self.pick_folder); add=QPushButton("Adicionar"); add.clicked.connect(self.add)
        for widget in (self.kind,self.frequency,self.format,self.folder,pick,add): form.addWidget(widget)
        root.addLayout(form); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["Relatório","Frequência","Formato","Próxima execução","Pasta"]); self.table.horizontalHeader().setSectionResizeMode(4,QHeaderView.Stretch); root.addWidget(self.table); remove=QPushButton("Remover selecionado"); remove.clicked.connect(self.remove); root.addWidget(remove); self.reload()
    def pick_folder(self):
        folder=QFileDialog.getExistingDirectory(self,"Pasta dos relatórios automáticos")
        if folder: self.folder.setText(folder)
    def add(self):
        try: add_schedule(self.kind.currentData(),self.frequency.currentText(),self.folder.text(),self.format.currentText()); self.reload()
        except Exception as exc: QMessageBox.warning(self,"Agendamento",str(exc))
    def remove(self):
        row=self.table.currentRow()
        if row >= 0: delete_schedule(row); self.reload()
    def reload(self):
        items=load_schedules(); self.table.setRowCount(len(items))
        for row,item in enumerate(items):
            values=(REPORTS.get(item["kind"],item["kind"]),item["frequency"],item.get("format","xlsx"),item["next_run"],item["folder"])
            for col,value in enumerate(values): self.table.setItem(row,col,QTableWidgetItem(str(value)))
