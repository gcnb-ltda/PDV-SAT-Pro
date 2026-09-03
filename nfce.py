from __future__ import annotations
import hashlib, uuid
from datetime import datetime
from sat import FiscalResult

class NfceSimulator:
    def __init__(self, config): self.config=config
    def status(self):
        env=self.config.get("environment","homologacao").upper()
        return f"NFC-e {env} — CONFIGURADA / SIMULADOR"
    def authorize(self, cart, payment):
        seed=f'{self.config.get("cnpj")}{datetime.now().isoformat()}{uuid.uuid4()}'
        key="SIM-NFCE-"+hashlib.sha256(seed.encode()).hexdigest()[:32].upper()
        return FiscalResult(True,key,"100|Autorizado o uso da NF-e|"+key)

class NfceSefaz:
    """Ponto de extensão para assinatura XML e autorização SEFAZ 4.00.

    Em produção, conecte uma biblioteca fiscal homologada aqui. A interface é
    intencionalmente igual à do SAT para que a tela de venda não dependa do emissor.
    """
    def __init__(self, config): self.config=config
    def status(self): return "NFC-e REAL — CONECTOR PENDENTE DE PROVEDOR FISCAL"
    def authorize(self, cart, payment):
        raise RuntimeError("Configure o provedor NFC-e homologado no adaptador NfceSefaz.")

def create_nfce(config):
    return NfceSefaz(config) if config.get("environment") == "producao" else NfceSimulator(config)
