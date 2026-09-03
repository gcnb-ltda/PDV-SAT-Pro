from qt_compat import QApplication
from config_dialog import FiscalConfigDialog

def test_fiscal_configuration_dialog_can_be_constructed():
    app=QApplication.instance() or QApplication([])
    dialog=FiscalConfigDialog()
    assert dialog.windowTitle()=="Configuração fiscal e ativação"
    assert dialog.stack.count()==2
    assert dialog.cnpj is not None
    assert dialog.cert is not None
    dialog.close()
