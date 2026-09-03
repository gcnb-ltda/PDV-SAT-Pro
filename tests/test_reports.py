from reports import ReportData, export_report


def test_export_report_formats(tmp_path):
    report=ReportData("Teste",["Produto","Total"],[["Item","R$ 10,00"]],"1 item","Hoje")
    for extension in ("csv","xlsx","pdf"):
        path=tmp_path/f"relatorio.{extension}"
        assert export_report(report,str(path)) == path
        assert path.exists() and path.stat().st_size > 0

def test_report_export_buttons_accept_qt5_signal_without_checked_argument():
    source=__import__("pathlib").Path("report_dialog.py").read_text(encoding="utf-8")
    assert 'lambda checked=False,e=ext:self.export(e)' in source
    assert 'self.export_buttons[ext]=button' in source
