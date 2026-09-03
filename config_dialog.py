from qt_compat import (QDialog,QFormLayout,QLineEdit,QComboBox,QPushButton,QHBoxLayout,
                       QVBoxLayout,QFileDialog,QLabel,QStackedWidget,QWidget,QMessageBox)
from settings import load_settings, save_settings, validate_fiscal_settings

class FiscalConfigDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Configuração fiscal"); self.resize(560,610)
        self.data=load_settings(); root=QVBoxLayout(self)
        root.addWidget(QLabel("EMISSOR FISCAL")); self.kind=QComboBox(); self.kind.addItems(["SAT","NFC-e"]); self.kind.setCurrentText(self.data["fiscal_type"]); root.addWidget(self.kind)
        common=QFormLayout(); self.cnpj=self.field("cnpj"); self.ie=self.field("ie"); self.uf=self.field("uf")
        self.env=QComboBox(); self.env.addItems(["homologacao","producao"]); self.env.setCurrentText(self.data["environment"])
        self.max_discount=self.field("max_discount_percent")
        self.company_name=self.field("company_name"); self.operator_name=self.field("operator_name"); self.report_role=QComboBox(); self.report_role.addItems(["ADMIN","GERENTE","OPERADOR"]); self.report_role.setCurrentText(self.data.get("report_role","ADMIN"))
        common.addRow("Razão social",self.company_name); common.addRow("CNPJ",self.cnpj); common.addRow("Inscrição Estadual",self.ie); common.addRow("UF",self.uf); common.addRow("Ambiente",self.env); common.addRow("Operador atual",self.operator_name); common.addRow("Perfil de relatórios",self.report_role); common.addRow("Desconto máximo (%)",self.max_discount); root.addLayout(common)
        self.stack=QStackedWidget(); self.stack.addWidget(self.sat_page()); self.stack.addWidget(self.nfce_page()); root.addWidget(self.stack)
        warning=QLabel("Credenciais são gravadas apenas neste computador. Restrinja o acesso ao usuário do sistema operacional e mantenha backup seguro do certificado."); warning.setWordWrap(True); warning.setStyleSheet("color:#d9b84c"); root.addWidget(warning)
        buttons=QHBoxLayout(); cancel=QPushButton("Cancelar"); save=QPushButton("Salvar configuração"); save.setObjectName("primary"); cancel.clicked.connect(self.reject); save.clicked.connect(self.persist); buttons.addWidget(cancel); buttons.addWidget(save); root.addLayout(buttons)
        self.kind.currentIndexChanged.connect(self.stack.setCurrentIndex); self.stack.setCurrentIndex(self.kind.currentIndex())
    def field(self,key,password=False):
        w=QLineEdit(str(self.data.get(key,"")))
        if password: w.setEchoMode(QLineEdit.Password)
        return w
    def sat_page(self):
        page=QWidget(); form=QFormLayout(page); self.sat_dll=self.field("sat_dll"); browse=QPushButton("Selecionar DLL"); browse.clicked.connect(self.pick_dll); box=QHBoxLayout(); box.addWidget(self.sat_dll); box.addWidget(browse)
        self.sat_code=self.field("sat_code",True); self.sat_number=self.field("sat_number"); form.addRow("DLL do fabricante",box); form.addRow("Código de ativação",self.sat_code); form.addRow("Número de sessão",self.sat_number); return page
    def nfce_page(self):
        page=QWidget(); form=QFormLayout(page); self.cert=self.field("nfce_certificate"); browse=QPushButton("Selecionar A1"); browse.clicked.connect(self.pick_cert); box=QHBoxLayout(); box.addWidget(self.cert); box.addWidget(browse)
        self.tax_regime=QComboBox(); self.tax_regime.addItems(["1 - Simples Nacional","2 - Simples excesso sublimite","3 - Regime normal","4 - MEI"]); self.tax_regime.setCurrentIndex(max(0,int(self.data.get("tax_regime","3"))-1))
        self.cert_pass=self.field("nfce_password",True); self.csc=self.field("nfce_csc",True); self.csc_id=self.field("nfce_csc_id"); self.series=self.field("nfce_series"); self.last=self.field("nfce_last_number")
        form.addRow("Integração","SEFAZ estadual direta"); form.addRow("Regime tributário (CRT)",self.tax_regime); form.addRow("Certificado A1 (.pfx/.p12)",box); form.addRow("Senha do certificado",self.cert_pass); form.addRow("CSC / token SEFAZ",self.csc); form.addRow("ID do CSC",self.csc_id); form.addRow("Série",self.series); form.addRow("Último número",self.last); return page
    def pick_dll(self): self.sat_dll.setText(QFileDialog.getOpenFileName(self,"DLL SAT",filter="DLL (*.dll)")[0])
    def pick_cert(self): self.cert.setText(QFileDialog.getOpenFileName(self,"Certificado A1",filter="Certificado (*.pfx *.p12)")[0])
    def persist(self):
        if not self.cnpj.text().strip(): QMessageBox.warning(self,"Configuração","Informe o CNPJ."); return
        values={"fiscal_type":self.kind.currentText(),"company_name":self.company_name.text(),"cnpj":self.cnpj.text(),"ie":self.ie.text(),"uf":self.uf.text().upper(),"environment":self.env.currentText(),"operator_name":self.operator_name.text() or "ADMIN","report_role":self.report_role.currentText(),"max_discount_percent":self.max_discount.text(),"sat_dll":self.sat_dll.text(),"sat_code":self.sat_code.text(),"sat_number":self.sat_number.text(),"nfce_provider":"SEFAZ Direta","tax_regime":str(self.tax_regime.currentIndex()+1),"nfce_certificate":self.cert.text(),"nfce_password":self.cert_pass.text(),"nfce_csc":self.csc.text(),"nfce_csc_id":self.csc_id.text(),"nfce_series":self.series.text(),"nfce_last_number":self.last.text()}
        try:
            percent=float(values["max_discount_percent"])
            if not 0 <= percent <= 100: raise ValueError("Desconto máximo deve estar entre 0 e 100%.")
            validate_fiscal_settings(values); save_settings(values); self.accept()
        except Exception as exc: QMessageBox.critical(self,"Configuração",str(exc))
