from __future__ import annotations
import urllib.request, urllib.error
from dataclasses import dataclass
from lxml import etree
from sefaz_endpoints import endpoint, ibge_uf_code

SOAP="http://www.w3.org/2003/05/soap-envelope"; NFE="http://www.portalfiscal.inf.br/nfe/wsdl"
@dataclass(frozen=True)
class SefazResponse:
    status:str; reason:str; protocol:str=""; receipt:str=""; xml:bytes=b""
    @property
    def authorized(self): return self.status in ("100","150")

class SefazSoapClient:
    def __init__(self,config,certificate,timeout=30): self.config=config; self.certificate=certificate; self.timeout=timeout
    def call(self,service:str,payload:bytes,soap_action:str=""):
        url=endpoint(self.config["uf"],self.config["environment"],service,self.config.get("sefaz_endpoints_json"))
        envelope=etree.Element(etree.QName(SOAP,"Envelope"),nsmap={"soap12":SOAP}); header=etree.SubElement(envelope,etree.QName(SOAP,"Header"))
        cab=etree.SubElement(header,etree.QName(NFE,"nfeCabecMsg")); etree.SubElement(cab,etree.QName(NFE,"cUF")).text=ibge_uf_code(self.config["uf"]); etree.SubElement(cab,etree.QName(NFE,"versaoDados")).text="4.00"
        body=etree.SubElement(envelope,etree.QName(SOAP,"Body")); data=etree.SubElement(body,etree.QName(NFE,"nfeDadosMsg")); data.append(etree.fromstring(payload))
        request=urllib.request.Request(url,etree.tostring(envelope,xml_declaration=True,encoding="utf-8"),headers={"Content-Type":f'application/soap+xml; charset=utf-8; action="{soap_action}"',"User-Agent":"PDV-SAT-Pro/1.0"},method="POST")
        try:
            with self.certificate.ssl_context() as context, urllib.request.urlopen(request,timeout=self.timeout,context=context) as response: raw=response.read()
        except urllib.error.HTTPError as exc: raise RuntimeError(f"SEFAZ HTTP {exc.code}: {exc.reason}") from exc
        except (urllib.error.URLError,TimeoutError) as exc: raise ConnectionError(f"Falha segura de comunicação com SEFAZ: {exc}") from exc
        return self.parse(raw)
    @staticmethod
    def parse(raw:bytes):
        root=etree.fromstring(raw); find=lambda name:root.xpath(f"string(.//*[local-name()='{name}'][1])")
        return SefazResponse(find("cStat"),find("xMotivo"),find("nProt"),find("nRec"),raw)

def status_request(config):
    ns="http://www.portalfiscal.inf.br/nfe"; root=etree.Element(f"{{{ns}}}consStatServ",nsmap={None:ns},versao="4.00")
    etree.SubElement(root,f"{{{ns}}}tpAmb").text="1" if config["environment"]=="producao" else "2"; etree.SubElement(root,f"{{{ns}}}cUF").text=ibge_uf_code(config["uf"]); etree.SubElement(root,f"{{{ns}}}xServ").text="STATUS"
    return etree.tostring(root,encoding="utf-8",xml_declaration=True)
