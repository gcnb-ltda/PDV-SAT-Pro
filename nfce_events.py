from __future__ import annotations
from datetime import datetime
from lxml import etree
from nfce_xml import NS,N,E,digits
from sefaz_endpoints import ibge_uf_code

def event_xml(config,key,protocol,sequence=1,event_type="110111",reason=""):
    root=etree.Element(N("envEvento"),nsmap={None:NS},versao="1.00"); E(root,"idLote",datetime.now().strftime("%Y%m%d%H%M%S")); ev=E(root,"evento",versao="1.00")
    ident="ID"+event_type+key+str(sequence).zfill(2); info=E(ev,"infEvento",Id=ident)
    for tag,val in (("cOrgao",ibge_uf_code(config["uf"])),("tpAmb","1" if config["environment"]=="producao" else "2"),("CNPJ",digits(config["cnpj"])),("chNFe",key),("dhEvento",datetime.now().astimezone().isoformat(timespec="seconds")),("tpEvento",event_type),("nSeqEvento",sequence),("verEvento","1.00")):E(info,tag,val)
    detail=E(info,"detEvento",versao="1.00"); E(detail,"descEvento","Cancelamento"); E(detail,"nProt",protocol); E(detail,"xJust",reason)
    return root

def inutilization_xml(config,year,series,start,end,reason):
    ident=f"ID{ibge_uf_code(config['uf'])}{str(year)[-2:]}{digits(config['cnpj'])}65{int(series):03d}{int(start):09d}{int(end):09d}"
    root=etree.Element(N("inutNFe"),nsmap={None:NS},versao="4.00"); info=E(root,"infInut",Id=ident)
    for tag,val in (("tpAmb","1" if config["environment"]=="producao" else "2"),("xServ","INUTILIZAR"),("cUF",ibge_uf_code(config["uf"])),("ano",str(year)[-2:]),("CNPJ",digits(config["cnpj"])),("mod","65"),("serie",int(series)),("nNFIni",int(start)),("nNFFin",int(end)),("xJust",reason)):E(info,tag,val)
    return root
