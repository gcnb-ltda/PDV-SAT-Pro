from qt_compat import (QDialog,QVBoxLayout,QFormLayout,QHBoxLayout,QComboBox,QSpinBox,QCheckBox,
    QLineEdit,QPushButton,QMessageBox,QLabel)
from settings import load_settings,save_settings
from printing import available_printers,print_html


class PrinterConfigDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Configuração da impressora"); self.resize(520,390); self.data=load_settings(); root=QVBoxLayout(self); root.addWidget(QLabel("IMPRESSORA DE CUPOM / EXTRATO FISCAL")); form=QFormLayout()
        self.printer=QComboBox(); self.printer.setEditable(True); self.printer.addItems(available_printers()); self.printer.setCurrentText(self.data.get("printer_name",""))
        self.paper=QComboBox(); self.paper.addItems(["58","80"]); self.paper.setCurrentText(str(self.data.get("printer_paper","80")))
        self.copies=QSpinBox(); self.copies.setRange(1,5); self.copies.setValue(int(self.data.get("printer_copies","1")))
        self.auto=QCheckBox("Imprimir automaticamente após venda autorizada"); self.auto.setChecked(bool(self.data.get("printer_auto",False)))
        self.header=QLineEdit(self.data.get("printer_header","")); self.footer=QLineEdit(self.data.get("printer_footer",""))
        form.addRow("Impressora",self.printer); form.addRow("Largura do papel (mm)",self.paper); form.addRow("Número de vias",self.copies); form.addRow("Cabeçalho adicional",self.header); form.addRow("Rodapé",self.footer); form.addRow("",self.auto); root.addLayout(form)
        info=QLabel("O SAT autoriza o CF-e e a impressora térmica imprime o extrato. Ambos são configurados separadamente."); info.setWordWrap(True); root.addWidget(info)
        buttons=QHBoxLayout(); test=QPushButton("Testar impressão"); save=QPushButton("Salvar"); save.setObjectName("primary"); cancel=QPushButton("Cancelar"); test.clicked.connect(self.test); save.clicked.connect(self.persist); cancel.clicked.connect(self.reject); buttons.addWidget(test); buttons.addStretch(); buttons.addWidget(cancel); buttons.addWidget(save); root.addLayout(buttons)
    def values(self):
        return {"printer_name":self.printer.currentText().strip(),"printer_paper":self.paper.currentText(),"printer_copies":str(self.copies.value()),"printer_auto":self.auto.isChecked(),"printer_header":self.header.text(),"printer_footer":self.footer.text()}
    def test(self):
        try:
            values=load_settings()|self.values(); html=f"<h2>{values.get('company_name','PDV SAT Pro')}</h2><p>TESTE DE IMPRESSÃO</p><p>Papel {values['printer_paper']} mm</p>"
            print_html(html,values,self,show_dialog=not bool(values["printer_name"])); QMessageBox.information(self,"Impressora","Teste enviado para a impressora.")
        except Exception as exc: QMessageBox.critical(self,"Impressora",str(exc))
    def persist(self):
        if not self.printer.currentText().strip(): QMessageBox.warning(self,"Impressora","Selecione ou informe uma impressora."); return
        try: save_settings(load_settings()|self.values()); self.accept()
        except Exception as exc: QMessageBox.critical(self,"Impressora",str(exc))
