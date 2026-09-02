from __future__ import annotations
import ctypes, os, uuid
from dataclasses import dataclass
from datetime import datetime
from xml.sax.saxutils import escape

@dataclass
class FiscalResult:
    success: bool
    key: str
    raw: str

class SatSimulator:
    def status(self): return "SAT SIMULADO — OPERACIONAL"
    def authorize(self, cart, payment):
        key = f"SIM-{datetime.now():%Y%m%d%H%M%S}-{uuid.uuid4().hex[:8].upper()}"
        return FiscalResult(True, key, "06000|Emitido com sucesso|" + key)

class SatDll:
    def __init__(self, config):
        path = config["sat_dll"]
        self.code = config["sat_code"]
        self.number = int(config.get("sat_number", "1"))
        self.dll = ctypes.WinDLL(path)
        for name in ("ConsultarSAT", "EnviarDadosVenda"):
            fn = getattr(self.dll, name)
            fn.restype = ctypes.c_char_p

    def status(self):
        raw = self.dll.ConsultarSAT(self.number).decode("utf-8", errors="replace")
        return raw

    def authorize(self, cart, payment):
        xml = build_cfe_xml(cart, payment).encode("utf-8")
        raw = self.dll.EnviarDadosVenda(self.number, self.code.encode(), xml)
        text = raw.decode("utf-8", errors="replace")
        parts = text.split("|")
        ok = len(parts) > 1 and parts[1] in {"06000", "6000"}
        key = next((p for p in parts if len(p) == 44 and p.isdigit()), "")
        return FiscalResult(ok, key, text)

def build_cfe_xml(cart, payment):
    details = "".join(
        f'<det nItem="{n}"><prod><cProd>{i.product.id}</cProd><xProd>{escape(i.product.name)}</xProd>'
        f'<NCM>{i.product.ncm}</NCM><CFOP>{i.product.cfop}</CFOP><uCom>UN</uCom>'
        f'<qCom>{i.quantity}</qCom><vUnCom>{i.product.price}</vUnCom></prod></det>'
        for n, i in enumerate(cart.items, 1))
    return f'<CFe><infCFe versaoDadosEnt="0.08"><detalhes>{details}</detalhes><pgto><MP><cMP>{escape(payment)}</cMP><vMP>{cart.total}</vMP></MP></pgto></infCFe></CFe>'

def create_sat(config=None):
    config = config or {}
    real = config.get("sat_dll") and config.get("sat_code")
    return SatDll(config) if real else SatSimulator()
