from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from sqlalchemy import text

from database import Session
from settings import load_settings


REPORTS = {
    "sales": "Vendas detalhadas",
    "cash": "Fechamento de caixa",
    "daily": "Resumo diário",
    "sold_products": "Produtos vendidos",
    "top_products": "Produtos mais vendidos",
    "no_movement": "Produtos sem movimentação",
    "stock": "Posição de estoque",
    "low_stock": "Estoque mínimo",
    "movements": "Movimentação de estoque",
    "profitability": "Rentabilidade",
    "discounts": "Descontos concedidos",
    "cancellations": "Cancelamentos",
    "payments": "Formas de pagamento",
    "operators": "Desempenho por operador",
    "fiscal_documents": "Documentos fiscais",
    "fiscal_errors": "Inconsistências fiscais",
    "taxes": "Base fiscal por NCM",
    "customers": "Clientes",
    "abc": "Curva ABC",
    "audit": "Auditoria",
}


@dataclass
class ReportData:
    title: str
    columns: list[str]
    rows: list[list]
    summary: str = ""
    filters: str = ""


def _period(start: date, end: date, alias="s"):
    return (f"date({alias}.created_at, 'localtime') BETWEEN :start AND :end", {"start": start.isoformat(), "end": end.isoformat()})


def _money(value):
    return f"R$ {Decimal(str(value or 0)):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _query(sql, params=None):
    with Session() as session:
        return [list(row) for row in session.execute(text(sql), params or {}).all()]


def generate_report(kind: str, start: date, end: date, search="", payment="Todos") -> ReportData:
    if kind not in REPORTS:
        raise ValueError("Relatório desconhecido.")
    period, params = _period(start, end)
    clauses = [period]
    if payment != "Todos":
        clauses.append("s.payment = :payment"); params["payment"] = payment
    where = " AND ".join(clauses)
    term = search.strip()
    filters = f"Período: {start:%d/%m/%Y} a {end:%d/%m/%Y}" + (f" | Busca: {term}" if term else "")

    if kind == "sales":
        rows=_query(f"SELECT s.id,s.created_at,s.operator,s.cash_register,s.payment,s.customer_document,s.subtotal,s.discount,s.total,s.fiscal_status FROM sales s WHERE {where} ORDER BY s.created_at DESC",params)
        for r in rows: r[6:9]=map(_money,r[6:9])
        return ReportData(REPORTS[kind],["Venda","Data","Operador","Caixa","Pagamento","CPF/CNPJ","Subtotal","Desconto","Total","Fiscal"],rows,f"{len(rows)} venda(s)",filters)
    if kind == "cash":
        rows=_query(f"SELECT s.cash_register,s.payment,COUNT(*),SUM(s.subtotal),SUM(s.discount),SUM(s.total) FROM sales s WHERE {where} AND s.status='CONCLUIDA' GROUP BY s.cash_register,s.payment ORDER BY s.cash_register,s.payment",params)
        for r in rows: r[3:6]=map(_money,r[3:6])
        return ReportData(REPORTS[kind],["Caixa","Pagamento","Vendas","Bruto","Descontos","Líquido"],rows,"Saldo inicial, suprimentos e sangrias permanecem zerados quando não registrados.",filters)
    if kind == "daily":
        rows=_query(f"SELECT date(s.created_at,'localtime'),COUNT(*),SUM(s.total),AVG(s.total),SUM((SELECT COALESCE(SUM(si.quantity),0) FROM sale_items si WHERE si.sale_id=s.id)) FROM sales s WHERE {where} AND s.status='CONCLUIDA' GROUP BY date(s.created_at,'localtime') ORDER BY date(s.created_at,'localtime') DESC",params)
        for r in rows: r[2]=_money(r[2]); r[3]=_money(r[3])
        return ReportData(REPORTS[kind],["Data","Vendas","Faturamento","Ticket médio","Itens"],rows,f"{len(rows)} dia(s)",filters)
    if kind in ("sold_products","top_products"):
        extra=" AND (si.description LIKE :term OR p.barcode LIKE :term)" if term else ""
        if term: params["term"]=f"%{term}%"
        rows=_query(f"SELECT p.barcode,si.description,p.category,SUM(si.quantity),SUM(si.total) FROM sale_items si JOIN sales s ON s.id=si.sale_id LEFT JOIN products p ON p.id=si.product_id WHERE {where} AND s.status='CONCLUIDA'{extra} GROUP BY p.barcode,si.description,p.category ORDER BY {'SUM(si.quantity) DESC' if kind=='top_products' else 'si.description'}",params)
        for r in rows: r[4]=_money(r[4])
        return ReportData(REPORTS[kind],["Código","Produto","Categoria","Quantidade","Faturamento"],rows,f"{len(rows)} produto(s)",filters)
    if kind == "no_movement":
        params.update({"term":f"%{term}%"})
        rows=_query("SELECT p.barcode,p.name,p.category,p.stock,p.unit FROM products p WHERE p.active=1 AND (p.name LIKE :term OR p.barcode LIKE :term) AND NOT EXISTS (SELECT 1 FROM sale_items si JOIN sales s ON s.id=si.sale_id WHERE si.product_id=p.id AND date(s.created_at,'localtime') BETWEEN :start AND :end) ORDER BY p.name",params)
        return ReportData(REPORTS[kind],["Código","Produto","Categoria","Estoque","Unidade"],rows,f"{len(rows)} produto(s) sem venda",filters)
    if kind in ("stock","low_stock"):
        condition=" AND p.stock <= p.min_stock" if kind=="low_stock" else ""
        params["term"]=f"%{term}%"
        rows=_query(f"SELECT p.barcode,p.name,p.category,p.stock,p.min_stock,p.unit,p.cost,p.price,(p.stock*p.cost),(p.stock*p.price) FROM products p WHERE p.active=1 AND (p.name LIKE :term OR p.barcode LIKE :term){condition} ORDER BY p.name",params)
        for r in rows:
            for idx in (6,7,8,9): r[idx]=_money(r[idx])
        return ReportData(REPORTS[kind],["Código","Produto","Categoria","Estoque","Mínimo","Un.","Custo","Preço","Valor custo","Venda potencial"],rows,f"{len(rows)} produto(s)",filters)
    if kind == "movements":
        params["term"]=f"%{term}%"
        rows=_query("SELECT m.id,m.created_at,p.barcode,p.name,m.movement_type,m.quantity,m.operator,m.reason,m.sale_id FROM stock_movements m JOIN products p ON p.id=m.product_id WHERE date(m.created_at,'localtime') BETWEEN :start AND :end AND (p.name LIKE :term OR p.barcode LIKE :term) ORDER BY m.created_at DESC",params)
        return ReportData(REPORTS[kind],["ID","Data","Código","Produto","Tipo","Quantidade","Operador","Motivo","Venda"],rows,f"{len(rows)} movimentação(ões)",filters)
    if kind == "profitability":
        params["term"]=f"%{term}%"
        rows=_query(f"SELECT p.barcode,si.description,p.category,SUM(si.quantity),SUM(si.total),SUM(si.quantity*p.cost),SUM(si.total-si.quantity*p.cost),CASE WHEN SUM(si.total)>0 THEN 100.0*SUM(si.total-si.quantity*p.cost)/SUM(si.total) ELSE 0 END FROM sale_items si JOIN sales s ON s.id=si.sale_id JOIN products p ON p.id=si.product_id WHERE {where} AND (p.name LIKE :term OR p.barcode LIKE :term) GROUP BY p.id ORDER BY SUM(si.total-si.quantity*p.cost) DESC",params)
        for r in rows:
            for idx in (4,5,6): r[idx]=_money(r[idx])
            r[7]=f"{float(r[7] or 0):.2f}%"
        return ReportData(REPORTS[kind],["Código","Produto","Categoria","Qtd.","Faturamento","Custo","Lucro bruto","Margem"],rows,"Margem calculada com o custo atual do cadastro.",filters)
    if kind == "discounts":
        rows=_query(f"SELECT s.id,s.created_at,s.operator,s.subtotal,s.discount,s.total FROM sales s WHERE {where} AND s.discount>0 ORDER BY s.created_at DESC",params)
        for r in rows: r[3:6]=map(_money,r[3:6])
        return ReportData(REPORTS[kind],["Venda","Data","Operador","Subtotal","Desconto","Total"],rows,f"{len(rows)} venda(s) com desconto",filters)
    if kind == "cancellations":
        rows=_query(f"SELECT s.id,s.created_at,s.operator,s.total,s.fiscal_key,s.fiscal_status FROM sales s WHERE {where} AND s.status='CANCELADA' ORDER BY s.created_at DESC",params)
        for r in rows: r[3]=_money(r[3])
        return ReportData(REPORTS[kind],["Venda","Data","Operador","Total","Documento","Fiscal"],rows,f"{len(rows)} cancelamento(s)",filters)
    if kind == "payments":
        rows=_query(f"SELECT s.payment,COUNT(*),SUM(s.total),AVG(s.total) FROM sales s WHERE {where} AND s.status='CONCLUIDA' GROUP BY s.payment ORDER BY SUM(s.total) DESC",params)
        for r in rows: r[2]=_money(r[2]); r[3]=_money(r[3])
        return ReportData(REPORTS[kind],["Pagamento","Vendas","Total","Ticket médio"],rows,"Consolidação por forma de pagamento",filters)
    if kind == "operators":
        rows=_query(f"SELECT s.operator,COUNT(*),SUM(s.total),AVG(s.total),SUM(s.discount),SUM(CASE WHEN s.status='CANCELADA' THEN 1 ELSE 0 END) FROM sales s WHERE {where} GROUP BY s.operator ORDER BY SUM(s.total) DESC",params)
        for r in rows:
            for idx in (2,3,4): r[idx]=_money(r[idx])
        return ReportData(REPORTS[kind],["Operador","Vendas","Total","Ticket médio","Descontos","Cancelamentos"],rows,"Desempenho por operador",filters)
    if kind in ("fiscal_documents","fiscal_errors"):
        error=" AND s.fiscal_status NOT IN ('AUTORIZADO','SIMULADO')" if kind=="fiscal_errors" else ""
        rows=_query(f"SELECT s.id,s.created_at,s.fiscal_type,s.fiscal_status,s.fiscal_key,s.total,s.customer_document FROM sales s WHERE {where}{error} ORDER BY s.created_at DESC",params)
        for r in rows: r[5]=_money(r[5])
        return ReportData(REPORTS[kind],["Venda","Data","Modelo","Situação","Chave/Protocolo","Total","CPF/CNPJ"],rows,f"{len(rows)} documento(s)",filters)
    if kind == "taxes":
        rows=_query(f"SELECT p.ncm,p.category,SUM(si.quantity),SUM(si.total) FROM sale_items si JOIN sales s ON s.id=si.sale_id JOIN products p ON p.id=si.product_id WHERE {where} GROUP BY p.ncm,p.category ORDER BY SUM(si.total) DESC",params)
        for r in rows: r[3]=_money(r[3])
        return ReportData(REPORTS[kind],["NCM","Categoria","Quantidade","Base de vendas"],rows,"Valores de tributos dependem do retorno fiscal homologado; este relatório consolida a base por NCM.",filters)
    if kind == "customers":
        rows=_query(f"SELECT s.customer_document,COUNT(*),SUM(s.total),AVG(s.total),MAX(s.created_at) FROM sales s WHERE {where} AND s.customer_document<>'' GROUP BY s.customer_document ORDER BY SUM(s.total) DESC",params)
        for r in rows: r[2]=_money(r[2]); r[3]=_money(r[3])
        return ReportData(REPORTS[kind],["CPF/CNPJ","Compras","Total","Ticket médio","Última compra"],rows,f"{len(rows)} cliente(s) identificado(s)",filters)
    if kind == "abc":
        rows=_query(f"SELECT p.barcode,si.description,SUM(si.quantity),SUM(si.total) FROM sale_items si JOIN sales s ON s.id=si.sale_id JOIN products p ON p.id=si.product_id WHERE {where} GROUP BY p.id ORDER BY SUM(si.total) DESC",params)
        total=sum(Decimal(str(r[3] or 0)) for r in rows); accumulated=Decimal("0")
        for r in rows:
            value=Decimal(str(r[3] or 0)); accumulated+=value; pct=(accumulated/total*100) if total else 0
            r.extend([f"{float(pct):.2f}%", "A" if pct <= 80 else "B" if pct <= 95 else "C"]); r[3]=_money(value)
        return ReportData(REPORTS[kind],["Código","Produto","Quantidade","Faturamento","Acumulado","Classe"],rows,"A até 80%, B até 95%, C acima de 95% do faturamento.",filters)
    return _audit_report(start,end,term)


def _audit_report(start, end, term):
    from platformdirs import user_log_dir
    log=Path(user_log_dir("PDV-SAT-Pro","GCNB"))/"pdv.log"
    rows=[]
    if log.exists():
        for line in log.read_text(encoding="utf-8",errors="replace").splitlines():
            try: stamp=datetime.strptime(line[:19],"%Y-%m-%d %H:%M:%S")
            except ValueError: continue
            if start <= stamp.date() <= end and (not term or term.lower() in line.lower()): rows.append([stamp,line[20:]])
    rows.reverse()
    return ReportData(REPORTS["audit"],["Data","Evento"],rows,f"{len(rows)} evento(s)",f"Período: {start:%d/%m/%Y} a {end:%d/%m/%Y}")


def export_report(report: ReportData, filename: str):
    path=Path(filename); suffix=path.suffix.lower()
    settings=load_settings(); metadata=[settings.get("company_name") or "Empresa não identificada",f"CNPJ: {settings.get('cnpj') or 'não informado'}",report.title,report.filters,report.summary,f"Gerado em: {datetime.now():%d/%m/%Y %H:%M} por {settings.get('operator_name','ADMIN')}"]
    if suffix == ".csv":
        with path.open("w",newline="",encoding="utf-8-sig") as fh:
            writer=csv.writer(fh,delimiter=";"); writer.writerows([[line] for line in metadata]); writer.writerow([]); writer.writerow(report.columns); writer.writerows(report.rows)
    elif suffix == ".xlsx":
        wb=Workbook(); ws=wb.active; ws.title="Relatório"
        for line in metadata: ws.append([line])
        ws.append([]); ws.append(report.columns)
        for row in report.rows: ws.append([str(value) if value is not None else "" for value in row])
        ws.freeze_panes="A8"; ws.auto_filter.ref=ws.dimensions
        for column in ws.columns: ws.column_dimensions[column[0].column_letter].width=min(45,max(12,max(len(str(cell.value or "")) for cell in column)+2))
        wb.save(path)
    elif suffix == ".pdf":
        styles=getSampleStyleSheet(); doc=SimpleDocTemplate(str(path),pagesize=landscape(A4),rightMargin=24,leftMargin=24,topMargin=24,bottomMargin=24)
        story=[Paragraph(report.title,styles["Title"]),Paragraph(report.filters,styles["Normal"]),Paragraph(report.summary,styles["Normal"]),Spacer(1,12)]
        data=[report.columns]+[[str(value) if value is not None else "" for value in row] for row in report.rows]
        table=Table(data,repeatRows=1); table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#f3c623")),("TEXTCOLOR",(0,0),(-1,0),colors.black),("GRID",(0,0),(-1,-1),0.25,colors.grey),("FONTSIZE",(0,0),(-1,-1),7),("VALIGN",(0,0),(-1,-1),"TOP")]))
        story.append(table); doc.build(story)
    else: raise ValueError("Use as extensões .pdf, .csv ou .xlsx.")
    return path
