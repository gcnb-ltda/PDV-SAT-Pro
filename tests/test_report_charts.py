from reports import REPORTS, ReportData
from report_charts import chart_for, number

def test_money_and_percent_values_are_converted_for_charts():
    assert number("R$ 1.234,56") == 1234.56
    assert number("42,50%") == 42.5

def test_all_twenty_reports_have_an_analytical_chart():
    row=["Venda 1","Produto A","Categoria","10","R$ 100,00","A","R$ 70,00","20%","R$ 120,00","AUTORIZADO"]
    for kind,title in REPORTS.items():
        chart=chart_for(kind,ReportData(title,[str(i) for i in range(10)],[row]))
        assert chart.title
        assert chart.chart_type in {"bar","line","pie"}
        assert chart.labels
        assert chart.series

def test_time_series_use_lines_and_composition_uses_pie():
    report=ReportData("Teste",[],[["01/09/2026","1","R$ 10,00","R$ 10,00","1"]])
    assert chart_for("daily",report).chart_type=="line"
    payment=ReportData("Teste",[],[["PIX","1","R$ 10,00","R$ 10,00"]])
    assert chart_for("payments",payment).chart_type=="pie"
