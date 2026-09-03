from __future__ import annotations
import hashlib, uuid
from datetime import datetime
from sat import FiscalResult

class NfceSimulator:
    def __init__(self, config): self.config=config
    def status(self):
        env=self.config.get("environment","homologacao").upper()
        return f"NFC-e {env} — CONFIGURADA / SIMULADOR"
    def authorize(self, cart, payment, customer_document=""):
        seed=f'{self.config.get("cnpj")}{datetime.now().isoformat()}{uuid.uuid4()}'
        key="SIM-NFCE-"+hashlib.sha256(seed.encode()).hexdigest()[:32].upper()
        return FiscalResult(True,key,"100|Autorizado o uso da NF-e|"+key)

class NfceSefaz:
    """Ponto de extensão para assinatura XML e autorização SEFAZ 4.00.

    Em produção, conecte uma biblioteca fiscal homologada aqui. A interface é
    intencionalmente igual à do SAT para que a tela de venda não dependa do emissor.
    """
    def __init__(self, config): self.config=config
    def status(self): return f"NFC-e SEFAZ DIRETA — {self.config.get('uf','').upper()} / {self.config.get('environment','').upper()}"
    def authorize(self, cart, payment, customer_document=""):
        raise RuntimeError("Emissão direta ainda não homologada: valide XML 4.00, assinatura, SOAP, QR Code e autorizador da UF antes de produção.")

def create_nfce(config):
    return NfceSefaz(config) if config.get("environment") == "producao" else NfceSimulator(config)
