from reports import ReportData, export_report


def test_export_report_formats(tmp_path):
    report=ReportData("Teste",["Produto","Total"],[["Item","R$ 10,00"]],"1 item","Hoje")
    for extension in ("csv","xlsx","pdf"):
        path=tmp_path/f"relatorio.{extension}"
        assert export_report(report,str(path)) == path
        assert path.exists() and path.stat().st_size > 0
