from decimal import Decimal
from domain import Cart,Product
from printing import receipt_html
from pathlib import Path


def test_receipt_contains_sale_and_customer():
    cart=Cart(); cart.add(Product(1,"789","Produto",Decimal("10"),Decimal("2")))
    html=receipt_html(cart,"PIX","SIM-123","52998224725",42,{"printer_paper":"80","company_name":"Empresa","cnpj":"00000000000100","printer_header":"","printer_footer":"Obrigado"})
    for value in ("Produto","52998224725","SIM-123","Venda #42","TOTAL R$ 10.00"):
        assert value in html

def test_linux_appimage_has_launcher_and_print_runtime_libraries():
    workflow=Path(".github/workflows/build-installers.yml").read_text(encoding="utf-8")
    assert "AppDir/AppRun" in workflow
    assert "libEGL.so.1" in workflow
    assert "libGL.so.1" in workflow
