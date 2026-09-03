from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

try:
    from PySide6.QtCore import Qt, QRectF, QPointF
    from PySide6.QtGui import QPainter, QColor, QPen, QFont
    from PySide6.QtWidgets import QWidget
except ImportError:
    from PySide2.QtCore import Qt, QRectF, QPointF
    from PySide2.QtGui import QPainter, QColor, QPen, QFont
    from PySide2.QtWidgets import QWidget

YELLOW=QColor("#f3c623"); GREEN=QColor("#56d6a0"); BLUE=QColor("#62a8ff")
GRID=QColor("#2b3445"); TEXT=QColor("#dce4ef"); MUTED=QColor("#8d9aab")

@dataclass
class ChartData:
    title: str
    chart_type: str
    labels: list[str]
    series: list[tuple[str,list[float]]]

def number(value):
    if value is None: return 0.0
    text=str(value).replace("R$","").replace("%","").strip()
    if "," in text: text=text.replace(".","").replace(",",".")
    try: return float(Decimal(text))
    except Exception: return 0.0

def _top(rows,label_index,value_indexes,limit=12):
    data=sorted(rows,key=lambda row:max(abs(number(row[i])) for i in value_indexes),reverse=True)[:limit]
    return [str(row[label_index])[:24] for row in data], [[number(row[i]) for row in data] for i in value_indexes]

def _counts(rows,index):
    values=defaultdict(float)
    for row in rows: values[str(row[index] or "Não informado")]+=1
    ordered=sorted(values.items(),key=lambda item:item[1],reverse=True)
    return [x[0] for x in ordered],[x[1] for x in ordered]

def chart_for(kind,report):
    rows=report.rows
    if kind=="sales": labels,vals=_top(rows,0,[8]); return ChartData("Valor das vendas","bar",labels,[("Total",vals[0])])
    if kind=="cash": labels,vals=_top(rows,1,[5]); return ChartData("Líquido por forma de pagamento","bar",labels,[("Líquido",vals[0])])
    if kind=="daily":
        data=sorted(rows,key=lambda r:str(r[0])); return ChartData("Evolução diária do faturamento","line",[str(r[0]) for r in data],[("Faturamento",[number(r[2]) for r in data])])
    if kind=="sold_products": labels,vals=_top(rows,1,[4]); return ChartData("Faturamento por produto","bar",labels,[("Faturamento",vals[0])])
    if kind=="top_products": labels,vals=_top(rows,1,[3]); return ChartData("Ranking por quantidade","bar",labels,[("Quantidade",vals[0])])
    if kind=="no_movement": labels,vals=_top(rows,1,[3]); return ChartData("Estoque de itens sem venda","bar",labels,[("Estoque",vals[0])])
    if kind in ("stock","low_stock"):
        labels,vals=_top(rows,1,[3,4]); return ChartData("Estoque atual versus mínimo","bar",labels,[("Atual",vals[0]),("Mínimo",vals[1])])
    if kind=="movements": labels,vals=_top(rows,3,[5]); return ChartData("Maiores movimentações de estoque","bar",labels,[("Quantidade",vals[0])])
    if kind=="profitability":
        labels,vals=_top(rows,1,[4,5,6]); return ChartData("Receita, custo e lucro por produto","bar",labels,[("Faturamento",vals[0]),("Custo",vals[1]),("Lucro",vals[2])])
    if kind=="discounts": labels,vals=_top(rows,0,[4]); return ChartData("Descontos por venda","bar",labels,[("Desconto",vals[0])])
    if kind=="cancellations": labels,vals=_top(rows,0,[3]); return ChartData("Valor das vendas canceladas","bar",labels,[("Total",vals[0])])
    if kind=="payments":
        labels=[str(r[0]) for r in rows]; return ChartData("Participação por forma de pagamento","pie",labels,[("Total",[number(r[2]) for r in rows])])
    if kind=="operators": labels,vals=_top(rows,0,[2]); return ChartData("Faturamento por operador","bar",labels,[("Total",vals[0])])
    if kind in ("fiscal_documents","fiscal_errors"):
        labels,vals=_counts(rows,3); return ChartData("Documentos por situação fiscal","pie",labels,[("Documentos",vals)])
    if kind=="taxes": labels,vals=_top(rows,0,[3]); return ChartData("Base de vendas por NCM","bar",labels,[("Base",vals[0])])
    if kind=="customers": labels,vals=_top(rows,0,[2]); return ChartData("Faturamento por cliente","bar",labels,[("Total",vals[0])])
    if kind=="abc":
        totals=defaultdict(float)
        for row in rows: totals[str(row[5])]+=number(row[3])
        labels=sorted(totals); return ChartData("Faturamento por classe ABC","pie",labels,[("Faturamento",[totals[x] for x in labels])])
    # Auditoria: eventos agregados por data.
    totals=defaultdict(float)
    for row in rows: totals[str(row[0])[:10]]+=1
    labels=sorted(totals); return ChartData("Eventos de auditoria por dia","line",labels,[("Eventos",[totals[x] for x in labels])])

class ReportChart(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent); self.data=None; self.setMinimumHeight(250)
    def set_data(self,data):
        self.data=data; self.setToolTip(data.title if data else "Sem dados para o gráfico"); self.update()
    def paintEvent(self,event):
        painter=QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(),QColor("#111620"))
        if not self.data or not self.data.labels or not any(self.data.series[0][1]):
            painter.setPen(MUTED); painter.drawText(self.rect(),Qt.AlignCenter,"Sem dados para representar no período"); return
        painter.setPen(TEXT); font=QFont(); font.setBold(True); font.setPointSize(11); painter.setFont(font); painter.drawText(18,26,self.data.title)
        area=QRectF(54,46,max(10,self.width()-76),max(10,self.height()-92))
        if self.data.chart_type=="pie": self._pie(painter,area)
        else: self._axes(painter,area)
    def _axes(self,p,area):
        all_values=[v for _,values in self.data.series for v in values]; low=min(0,min(all_values)); high=max(all_values)
        span=high-low or 1; p.setPen(QPen(GRID,1))
        for i in range(5):
            y=area.bottom()-area.height()*i/4; p.drawLine(QPointF(area.left(),y),QPointF(area.right(),y))
            p.setPen(MUTED); p.drawText(QRectF(0,y-9,50,18),Qt.AlignRight|Qt.AlignVCenter,f"{low+span*i/4:,.0f}"); p.setPen(QPen(GRID,1))
        count=len(self.data.labels); colors=(YELLOW,GREEN,BLUE)
        if self.data.chart_type=="line":
            for si,(name,values) in enumerate(self.data.series):
                points=[QPointF(area.left()+(area.width()*i/max(1,count-1)),area.bottom()-(v-low)/span*area.height()) for i,v in enumerate(values)]
                p.setPen(QPen(colors[si%3],3))
                for a,b in zip(points,points[1:]): p.drawLine(a,b)
                p.setBrush(colors[si%3])
                for point in points: p.drawEllipse(point,3,3)
        else:
            group=area.width()/max(1,count); bar=group*.72/max(1,len(self.data.series))
            for si,(_,values) in enumerate(self.data.series):
                p.setBrush(colors[si%3]); p.setPen(Qt.NoPen)
                for i,value in enumerate(values):
                    zero=area.bottom()-(-low/span)*area.height(); y=area.bottom()-(value-low)/span*area.height()
                    p.drawRoundedRect(QRectF(area.left()+i*group+group*.14+si*bar,min(y,zero),bar*.88,max(1,abs(zero-y))),2,2)
        p.setPen(MUTED); p.setFont(QFont("",7))
        for i,label in enumerate(self.data.labels):
            if count<=12: p.drawText(QRectF(area.left()+i*area.width()/count,area.bottom()+5,area.width()/count,30),Qt.AlignHCenter|Qt.AlignTop,label[:12])
        self._legend(p,area,colors)
    def _pie(self,p,area):
        values=self.data.series[0][1]; total=sum(values) or 1; size=min(area.width(),area.height()); pie=QRectF(area.left(),area.top(),size,size)
        colors=(YELLOW,GREEN,BLUE,QColor("#cf7bff"),QColor("#ff826e"),QColor("#55d5dc")); start=0
        for i,value in enumerate(values):
            angle=int(5760*value/total); p.setBrush(colors[i%len(colors)]); p.setPen(QPen(QColor("#111620"),2)); p.drawPie(pie,start,angle); start+=angle
        p.setPen(TEXT); x=pie.right()+18
        for i,(label,value) in enumerate(zip(self.data.labels,values)):
            p.setBrush(colors[i%len(colors)]); p.drawRect(QRectF(x,area.top()+i*22,10,10)); p.drawText(QRectF(x+16,area.top()+i*22-4,max(40,area.right()-x-18),18),Qt.AlignLeft|Qt.AlignVCenter,f"{label}: {value/total*100:.1f}%")
    def _legend(self,p,area,colors):
        x=area.left()
        for i,(name,_) in enumerate(self.data.series):
            p.setBrush(colors[i%3]); p.setPen(Qt.NoPen); p.drawRect(QRectF(x,32,10,10)); p.setPen(TEXT); p.drawText(QRectF(x+14,27,120,20),Qt.AlignLeft|Qt.AlignVCenter,name); x+=135
