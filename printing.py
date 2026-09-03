from __future__ import annotations

from datetime import datetime
from html import escape
from settings import load_settings


def receipt_html(cart, payment, fiscal_key="", customer_document="", sale_id="", config=None):
    config=config or load_settings(); width=int(config.get("printer_paper","80")); font=9 if width==58 else 10
    rows="".join(
        f"<tr><td>{escape(item.product.name)}</td><td align='right'>{item.quantity}</td>"
        f"<td align='right'>{item.product.price:.2f}</td><td align='right'>{item.total:.2f}</td></tr>"
        for item in cart.items)
    customer=f"<p><b>Cliente:</b> {escape(customer_document)}</p>" if customer_document else "<p>CONSUMIDOR NÃO IDENTIFICADO</p>"
    fiscal=f"<p><b>Documento fiscal:</b><br>{escape(fiscal_key)}</p>" if fiscal_key else ""
    return f"""<html><head><meta charset='utf-8'><style>
    body{{font-family:monospace;font-size:{font}px;color:#000}} h2,p{{text-align:center;margin:4px}}
    table{{width:100%;border-collapse:collapse}} th{{border-bottom:1px dashed #000}} td{{padding:2px}}
    .total{{font-size:{font+4}px;font-weight:bold;text-align:right;border-top:1px dashed #000}}
    </style></head><body><h2>{escape(config.get('company_name') or 'PDV SAT Pro')}</h2>
    <p>{escape(config.get('printer_header') or '')}</p><p>CNPJ: {escape(config.get('cnpj') or '')}</p>
    <p>Venda #{escape(str(sale_id))} — {datetime.now():%d/%m/%Y %H:%M}</p>{customer}
    <table><tr><th>Item</th><th>Qtd</th><th>Unit.</th><th>Total</th></tr>{rows}
    <tr><td colspan='3'>Subtotal</td><td align='right'>{cart.subtotal:.2f}</td></tr>
    <tr><td colspan='3'>Desconto</td><td align='right'>{cart.discount:.2f}</td></tr>
    <tr><td colspan='4' class='total'>TOTAL R$ {cart.total:.2f}</td></tr></table>
    <p>Pagamento: {escape(payment)}</p>{fiscal}<p>{escape(config.get('printer_footer') or '')}</p></body></html>"""


def available_printers():
    try:
        from PySide6.QtPrintSupport import QPrinterInfo
    except ImportError:
        from PySide2.QtPrintSupport import QPrinterInfo
    return [printer.printerName() for printer in QPrinterInfo.availablePrinters()]


def print_html(html, config=None, parent=None, show_dialog=False):
    config=config or load_settings()
    try:
        from PySide6.QtCore import QSizeF
        from PySide6.QtGui import QTextDocument, QPageSize
        from PySide6.QtPrintSupport import QPrinter, QPrintDialog
        qt6=True
    except ImportError:
        from PySide2.QtCore import QSizeF
        from PySide2.QtGui import QTextDocument
        from PySide2.QtPrintSupport import QPrinter, QPrintDialog
        qt6=False
    printer=QPrinter(QPrinter.HighResolution); name=config.get("printer_name","")
    if name: printer.setPrinterName(name)
    width=float(config.get("printer_paper","80")); printer.setCopyCount(int(config.get("printer_copies","1")))
    if qt6: printer.setPageSize(QPageSize(QSizeF(width,297),QPageSize.Millimeter,"Térmica"))
    else: printer.setPaperSize(QSizeF(width,297),QPrinter.Millimeter)
    if show_dialog:
        dialog=QPrintDialog(printer,parent)
        accepted=dialog.exec() if qt6 else dialog.exec_()
        if not accepted: return False
    document=QTextDocument(); document.setHtml(html); document.print_(printer); return True


def print_receipt(cart, payment, fiscal_key="", customer_document="", sale_id="", parent=None, show_dialog=False):
    config=load_settings()
    if not config.get("printer_name") and not show_dialog: raise RuntimeError("Selecione uma impressora nas configurações.")
    return print_html(receipt_html(cart,payment,fiscal_key,customer_document,sale_id,config),config,parent,show_dialog)
