from __future__ import annotations
import hashlib, uuid
from datetime import datetime
from lxml import etree
from sat import FiscalResult
from fiscal_certificate import A1Certificate
from fiscal_storage import enqueue, save_document
from nfce_events import event_xml, inutilization_xml
from nfce_xml import NS, N, E, add_supplement, build_nfce, serialize
from sefaz_soap import SefazSoapClient, status_request
from xsd_validator import validate_xml
from database import reserve_nfce_number
from copy import deepcopy

class NfceSimulator:
    def __init__(self,config): self.config=config
    def status(self): return f"NFC-e {self.config.get('environment','homologacao').upper()} — SIMULADOR (SEM VALOR FISCAL)"
    def authorize(self,cart,payment,customer_document=""):
        seed=f'{self.config.get("cnpj")}{datetime.now().isoformat()}{uuid.uuid4()}'
        key="SIM-NFCE-"+hashlib.sha256(seed.encode()).hexdigest()[:32].upper()
        return FiscalResult(True,key,"100|SIMULAÇÃO sem valor fiscal|"+key)

class NfceSefaz:
    """Emissor direto SEFAZ, sem provedor fiscal intermediário."""
    def __init__(self,config):
        self.config=config; self.certificate=A1Certificate(config["nfce_certificate"],config["nfce_password"]); self.client=SefazSoapClient(config,self.certificate)
    def _require_release(self):
        if not self.config.get("sefaz_homologation_approved",False):
            raise RuntimeError("Motor fiscal implementado, mas bloqueado: conclua os testes com a SEFAZ e marque a homologação aprovada.")
    def status(self):
        try:
            response=self.client.call("status",status_request(self.config),"NFeStatusServico4")
            return f"NFC-e SEFAZ {self.config['uf']} — {response.status} {response.reason}"
        except Exception as exc: return f"NFC-e SEFAZ {self.config['uf']} — INDISPONÍVEL: {exc}"
    def authorize(self,cart,payment,customer_document=""):
        self._require_release(); number=reserve_nfce_number(int(self.config["nfce_series"]),int(self.config.get("nfce_last_number",0))); root,key,number=build_nfce(self.config,cart,payment,customer_document,number=number)
        add_supplement(root,key,self.config); self.certificate.sign_inf_nfe(root); nfe_raw=serialize(root)
        validate_xml(nfe_raw,"nfe_v4.00.xsd",self.config.get("schema_dir"))
        batch=etree.Element(N("enviNFe"),nsmap={None:NS},versao="4.00"); E(batch,"idLote",datetime.now().strftime("%Y%m%d%H%M%S")); E(batch,"indSinc","1"); batch.append(root)
        batch_raw=serialize(batch); validate_xml(batch_raw,"enviNFe_v4.00.xsd",self.config.get("schema_dir"))
        try: response=self.client.call("authorization",batch_raw,"NFeAutorizacao4")
        except ConnectionError:
            if not self.config.get("nfce_offline_enabled",True): raise
            offline,key,number=build_nfce(self.config,cart,payment,customer_document,number=number,emission_type="9")
            add_supplement(offline,key,self.config,"9"); self.certificate.sign_inf_nfe(offline); raw=serialize(offline)
            validate_xml(raw,"nfe_v4.00.xsd",self.config.get("schema_dir"))
            path=enqueue(key,raw,{"number":number,"series":self.config["nfce_series"],"status":"PENDING_TRANSMISSION"})
            return FiscalResult(True,key,f"OFFLINE|Pendente de transmissão|{path}")
        save_document("responses",key,response.xml,{"cStat":response.status,"reason":response.reason,"protocol":response.protocol})
        if not response.authorized: return FiscalResult(False,key,f"{response.status}|{response.reason}")
        response_root=etree.fromstring(response.xml); protocols=response_root.xpath(".//*[local-name()='protNFe']")
        if not protocols: raise RuntimeError("SEFAZ informou autorização sem protNFe; resposta preservada para auditoria.")
        proc=etree.Element(N("nfeProc"),nsmap={None:NS},versao="4.00"); proc.append(root); proc.append(deepcopy(protocols[0]))
        proc_raw=serialize(proc); validate_xml(proc_raw,"procNFe_v4.00.xsd",self.config.get("schema_dir"))
        path=save_document("authorized",key,proc_raw,{"protocol":response.protocol,"number":number,"response_saved":True})
        return FiscalResult(True,key,f"{response.status}|{response.reason}|{response.protocol}|{path}")
    def cancel(self,key,protocol,reason):
        self._require_release()
        if len(reason.strip())<15: raise ValueError("Justificativa de cancelamento deve ter ao menos 15 caracteres.")
        root=event_xml(self.config,key,protocol,reason=reason); self.certificate.sign_inf_nfe(root[1]); raw=serialize(root)
        validate_xml(raw,"envEvento_v1.00.xsd",self.config.get("schema_dir")); response=self.client.call("event",raw,"NFeRecepcaoEvento4")
        save_document("events/cancellation",key,response.xml,{"cStat":response.status,"protocol":response.protocol}); return response
    def inutilize(self,year,series,start,end,reason):
        self._require_release()
        if len(reason.strip())<15: raise ValueError("Justificativa de inutilização deve ter ao menos 15 caracteres.")
        root=inutilization_xml(self.config,year,series,start,end,reason); self.certificate.sign_inf_nfe(root); raw=serialize(root)
        validate_xml(raw,"inutNFe_v4.00.xsd",self.config.get("schema_dir")); response=self.client.call("inutilization",raw,"NFeInutilizacao4")
        save_document("events/inutilization",root[0].get("Id","range"),response.xml,{"cStat":response.status,"protocol":response.protocol}); return response

def create_nfce(config):
    return NfceSefaz(config) if config.get("nfce_direct_enabled",False) else NfceSimulator(config)
