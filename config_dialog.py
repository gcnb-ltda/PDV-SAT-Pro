from qt_compat import (QDialog,QFormLayout,QLineEdit,QComboBox,QPushButton,QHBoxLayout,
                       QVBoxLayout,QFileDialog,QLabel,QStackedWidget,QWidget,QMessageBox,QCheckBox,
                       QScrollArea)
from settings import load_settings, save_settings, validate_fiscal_settings, fiscal_fingerprint
from fiscal_certificate import A1Certificate
from sefaz_soap import SefazSoapClient, status_request

class FiscalConfigDialog(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent); self.setWindowTitle("Configuração fiscal e ativação"); self.resize(720,850)
        self.data=load_settings(); root=QVBoxLayout(self)
        scroll=QScrollArea(); scroll.setWidgetResizable(True); body=QWidget(); content=QVBoxLayout(body)
        scroll.setWidget(body); root.addWidget(scroll)
        content.addWidget(QLabel("EMISSOR FISCAL")); self.kind=QComboBox(); self.kind.addItems(["SAT","NFC-e"]); self.kind.setCurrentText(self.data["fiscal_type"]); content.addWidget(self.kind)
        common=QFormLayout(); self.cnpj=self.field("cnpj"); self.ie=self.field("ie"); self.uf=self.field("uf")
        self.trade_name=self.field("trade_name"); self.street=self.field("street"); self.address_number=self.field("address_number"); self.district=self.field("district"); self.cep=self.field("cep"); self.municipality_code=self.field("municipality_code"); self.municipality_name=self.field("municipality_name")
        self.env=QComboBox(); self.env.addItems(["homologacao","producao"]); self.env.setCurrentText(self.data["environment"])
        self.max_discount=self.field("max_discount_percent")
        self.company_name=self.field("company_name"); self.operator_name=self.field("operator_name"); self.report_role=QComboBox(); self.report_role.addItems(["ADMIN","GERENTE","OPERADOR"]); self.report_role.setCurrentText(self.data.get("report_role","ADMIN"))
        common.addRow("Razão social",self.company_name); common.addRow("Nome fantasia",self.trade_name); common.addRow("CNPJ",self.cnpj); common.addRow("Inscrição Estadual",self.ie); common.addRow("UF",self.uf); common.addRow("Município",self.municipality_name); common.addRow("Código IBGE município",self.municipality_code); common.addRow("Logradouro",self.street); common.addRow("Número",self.address_number); common.addRow("Bairro",self.district); common.addRow("CEP",self.cep); common.addRow("Ambiente",self.env); common.addRow("Operador atual",self.operator_name); common.addRow("Perfil de relatórios",self.report_role); common.addRow("Desconto máximo (%)",self.max_discount); content.addLayout(common)
        self.stack=QStackedWidget(); self.stack.addWidget(self.sat_page()); self.stack.addWidget(self.nfce_page()); content.addWidget(self.stack)
        warning=QLabel("Credenciais são gravadas apenas neste computador. Restrinja o acesso ao usuário do sistema operacional e mantenha backup seguro do certificado."); warning.setWordWrap(True); warning.setStyleSheet("color:#d9b84c"); content.addWidget(warning)
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
        self.cert_pass=self.field("nfce_password",True); self.csc=self.field("nfce_csc",True); self.csc_id=self.field("nfce_csc_id"); self.series=self.field("nfce_series"); self.last=self.field("nfce_last_number"); self.qrcode_url=self.field("nfce_qrcode_url"); self.consult_url=self.field("nfce_consult_url"); self.schema_dir=self.field("schema_dir")
        self.credentialed=QCheckBox("Estabelecimento credenciado para NFC-e nesta UF"); self.credentialed.setChecked(bool(self.data.get("sefaz_credentialed",False)))
        self.enable_real=QCheckBox("Ativar emissão fiscal real neste computador"); self.enable_real.setChecked(bool(self.data.get("nfce_direct_enabled",False)))
        self.test_status=QLabel("Teste SEFAZ ainda não executado"); self.test_status.setWordWrap(True)
        test=QPushButton("Validar certificado, schemas e conexão SEFAZ"); test.clicked.connect(self.test_sefaz)
        integration=QLabel("SEFAZ estadual direta")
        form.addRow("Integração",integration); form.addRow("Regime tributário (CRT)",self.tax_regime); form.addRow("Certificado A1 (.pfx/.p12)",box); form.addRow("Senha do certificado",self.cert_pass); form.addRow("CSC / token SEFAZ",self.csc); form.addRow("ID do CSC",self.csc_id); form.addRow("Série",self.series); form.addRow("Último número",self.last); form.addRow("URL QR Code da UF",self.qrcode_url); form.addRow("URL de consulta",self.consult_url); form.addRow("Diretório de schemas oficiais",self.schema_dir); form.addRow(self.credentialed); form.addRow(test); form.addRow(self.test_status); form.addRow(self.enable_real); return page
    def pick_dll(self): self.sat_dll.setText(QFileDialog.getOpenFileName(self,"DLL SAT",filter="DLL (*.dll)")[0])
    def pick_cert(self): self.cert.setText(QFileDialog.getOpenFileName(self,"Certificado A1",filter="Certificado (*.pfx *.p12)")[0])
    def values(self):
        return {"fiscal_type":self.kind.currentText(),"company_name":self.company_name.text(),"trade_name":self.trade_name.text(),"cnpj":self.cnpj.text(),"ie":self.ie.text(),"uf":self.uf.text().upper(),"municipality_name":self.municipality_name.text(),"municipality_code":self.municipality_code.text(),"street":self.street.text(),"address_number":self.address_number.text(),"district":self.district.text(),"cep":self.cep.text(),"environment":self.env.currentText(),"operator_name":self.operator_name.text() or "ADMIN","report_role":self.report_role.currentText(),"max_discount_percent":self.max_discount.text(),"sat_dll":self.sat_dll.text(),"sat_code":self.sat_code.text(),"sat_number":self.sat_number.text(),"nfce_provider":"SEFAZ Direta","tax_regime":str(self.tax_regime.currentIndex()+1),"nfce_certificate":self.cert.text(),"nfce_password":self.cert_pass.text(),"nfce_csc":self.csc.text(),"nfce_csc_id":self.csc_id.text(),"nfce_series":self.series.text(),"nfce_last_number":self.last.text(),"nfce_qrcode_url":self.qrcode_url.text(),"nfce_consult_url":self.consult_url.text(),"schema_dir":self.schema_dir.text(),"nfce_direct_enabled":self.enable_real.isChecked(),"sefaz_credentialed":self.credentialed.isChecked(),"sefaz_homologation_approved":self.data.get("sefaz_homologation_approved",False),"sefaz_validation_fingerprint":self.data.get("sefaz_validation_fingerprint","")}
    def test_sefaz(self):
        try:
            values=self.values(); values["nfce_direct_enabled"]=False
            if not self.credentialed.isChecked(): raise ValueError("Confirme primeiro o credenciamento NFC-e do estabelecimento.")
            required=("cnpj","ie","uf","municipality_code","nfce_certificate","nfce_password","nfce_csc","nfce_csc_id","nfce_qrcode_url","nfce_consult_url","schema_dir")
            missing=[key for key in required if not str(values.get(key,"")).strip()]
            if missing: raise ValueError("Preencha os campos obrigatórios: "+", ".join(missing))
            certificate=A1Certificate(values["nfce_certificate"],values["nfce_password"])
            response=SefazSoapClient(values,certificate).call("status",status_request(values),"NFeStatusServico4")
            if response.status != "107": raise RuntimeError(f"SEFAZ retornou {response.status}: {response.reason}")
            self.data["sefaz_homologation_approved"]=True; self.data["sefaz_validation_fingerprint"]=fiscal_fingerprint(values)
            self.test_status.setText("Aprovado: SEFAZ 107 — Serviço em operação. A emissão real pode ser ativada.")
            self.test_status.setStyleSheet("color:#7ee2a8")
        except Exception as exc:
            self.data["sefaz_homologation_approved"]=False; self.data["sefaz_validation_fingerprint"]=""; self.enable_real.setChecked(False)
            self.test_status.setText("Falha: "+str(exc)); self.test_status.setStyleSheet("color:#ff7b7b")
    def persist(self):
        if not self.cnpj.text().strip(): QMessageBox.warning(self,"Configuração","Informe o CNPJ."); return
        values=self.values()
        try:
            percent=float(values["max_discount_percent"])
            if not 0 <= percent <= 100: raise ValueError("Desconto máximo deve estar entre 0 e 100%.")
            validate_fiscal_settings(values); save_settings(values); self.accept()
        except Exception as exc: QMessageBox.critical(self,"Configuração",str(exc))
