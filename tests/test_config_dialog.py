from qt_compat import QApplication, QPushButton
from config_dialog import FiscalConfigDialog
from dialogs import ProductEditDialog

def test_fiscal_configuration_dialog_can_be_constructed():
    app=QApplication.instance() or QApplication([])
    dialog=FiscalConfigDialog()
    assert dialog.windowTitle()=="Configuração fiscal e ativação"
    assert dialog.stack.count()==2
    assert dialog.cnpj is not None
    assert dialog.cert is not None
    dialog.close()

def test_product_dialog_has_save_action():
    app=QApplication.instance() or QApplication([])
    dialog=ProductEditDialog()
    assert any(button.text()=="Salvar produto" for button in dialog.findChildren(QPushButton))
    dialog.close()
