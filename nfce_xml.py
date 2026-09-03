from __future__ import annotations
import hashlib, re, secrets
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from lxml import etree
from sefaz_endpoints import ibge_uf_code

NS="http://www.portalfiscal.inf.br/nfe"; N=lambda tag:f"{{{NS}}}{tag}"
PAYMENTS={"Dinheiro":"01","Cartão de crédito":"03","Cartão de débito":"04","PIX":"17"}

def digits(value): return re.sub(r"\D","",str(value or ""))
def q(value,places="0.01"): return Decimal(str(value)).quantize(Decimal(places),rounding=ROUND_HALF_UP)
def dv43(base43):
    total=sum(int(n)*w for n,w in zip(reversed(base43),[2,3,4,5,6,7,8,9]*6)); d=11-total%11
    return "0" if d in (10,11) else str(d)
def access_key(config, number:int, issued:datetime, emission_type="1", numeric_code=None):
    base=(ibge_uf_code(config["uf"])+issued.strftime("%y%m")+digits(config["cnpj"]).zfill(14)+"65"+
          str(int(config["nfce_series"])).zfill(3)+str(number).zfill(9)+emission_type+(numeric_code or f"{secrets.randbelow(10**8):08d}"))
    if len(base)!=43: raise ValueError("Dados inválidos para gerar chave NFC-e.")
    return base+dv43(base)
def E(parent,tag,text=None,**attrs):
    node=etree.SubElement(parent,N(tag),**attrs)
    if text is not None: node.text=str(text)
    return node

def build_nfce(config,cart,payment,customer_document="",number=None,issued=None,emission_type="1"):
    issued=issued or datetime.now().astimezone(); number=int(number or int(config.get("nfce_last_number",0))+1)
    key=access_key(config,number,issued,emission_type); root=etree.Element(N("NFe"),nsmap={None:NS}); inf=E(root,"infNFe",Id="NFe"+key,versao="4.00")
    ide=E(inf,"ide");
    for tag,val in (("cUF",key[:2]),("cNF",key[35:43]),("natOp","VENDA"),("mod","65"),("serie",int(config["nfce_series"])),("nNF",number),("dhEmi",issued.isoformat(timespec="seconds")),("tpNF","1"),("idDest","1"),("cMunFG",digits(config["municipality_code"])),("tpImp","4"),("tpEmis",emission_type),("cDV",key[-1]),("tpAmb","1" if config["environment"]=="producao" else "2"),("finNFe","1"),("indFinal","1"),("indPres","1"),("procEmi","0"),("verProc","PDV-SAT-Pro 1.0")): E(ide,tag,val)
    emit=E(inf,"emit"); E(emit,"CNPJ",digits(config["cnpj"])); E(emit,"xNome",config["company_name"]); E(emit,"xFant",config.get("trade_name") or config["company_name"])
    addr=E(emit,"enderEmit")
    for tag,val in (("xLgr",config["street"]),("nro",config["address_number"]),("xBairro",config["district"]),("cMun",digits(config["municipality_code"])),("xMun",config["municipality_name"]),("UF",config["uf"]),("CEP",digits(config.get("cep"))),("cPais","1058"),("xPais","BRASIL")): 
        if val:E(addr,tag,val)
    E(emit,"IE",digits(config["ie"])); E(emit,"CRT",config["tax_regime"])
    if customer_document:
        dest=E(inf,"dest"); E(dest,"CPF" if len(digits(customer_document))==11 else "CNPJ",digits(customer_document)); E(dest,"indIEDest","9")
    total_products=Decimal("0"); total_tax=Decimal("0")
    for index,item in enumerate(cart.items,1):
        p=item.product; item_total=q(p.price*item.quantity); total_products+=item_total
        det=E(inf,"det",nItem=str(index)); prod=E(det,"prod")
        for tag,val in (("cProd",p.barcode or str(p.id)),("cEAN",p.barcode if len(digits(p.barcode)) in (8,12,13,14) else "SEM GTIN"),("xProd",p.name),("NCM",digits(p.ncm)),("CEST",digits(p.cest)),("CFOP",p.cfop),("uCom",p.unit),("qCom",f"{q(item.quantity,'0.0000'):.4f}"),("vUnCom",f"{q(p.price,'0.0000000000'):.10f}"),("vProd",f"{item_total:.2f}"),("cEANTrib","SEM GTIN"),("uTrib",p.unit),("qTrib",f"{q(item.quantity,'0.0000'):.4f}"),("vUnTrib",f"{q(p.price,'0.0000000000'):.10f}"),("indTot","1")):
            if val:E(prod,tag,val)
        tax=E(det,"imposto"); icms=E(tax,"ICMS"); crt=str(config["tax_regime"]); code=(p.icms_cst or ("102" if crt in ("1","4") else "00")).zfill(2 if crt=="3" else 3)
        group=E(icms,("ICMSSN" if crt in ("1","4") else "ICMS")+code); E(group,"orig",p.origin or "0"); E(group,"CSOSN" if crt in ("1","4") else "CST",code)
        if crt=="3" and code=="00":
            rate=q(p.icms_rate,'0.0000'); amount=q(item_total*rate/100); total_tax+=amount
            E(group,"modBC","3"); E(group,"vBC",f"{item_total:.2f}"); E(group,"pICMS",f"{rate:.4f}"); E(group,"vICMS",f"{amount:.2f}")
        for taxname,cst,rate in (("PIS",p.pis_cst or "07",p.pis_rate),("COFINS",p.cofins_cst or "07",p.cofins_rate)):
            outer=E(tax,taxname); cst=str(cst).zfill(2); grp=E(outer,taxname+("Aliq" if cst in ("01","02") else "NT")); E(grp,"CST",cst)
            if cst in ("01","02"): E(grp,"vBC",f"{item_total:.2f}"); E(grp,"p"+taxname,f"{q(rate,'0.0000'):.4f}"); E(grp,"v"+taxname,f"{q(item_total*Decimal(str(rate))/100):.2f}")
        # NT 2025.002 (RTC): o grupo somente é emitido quando a classificação
        # oficial foi cadastrada; nenhuma alíquota legal é presumida pelo PDV.
        if p.ibscbs_cst and p.tax_classification:
            rtc=E(tax,"IBSCBS"); E(rtc,"CST",p.ibscbs_cst); E(rtc,"cClassTrib",p.tax_classification); group=E(rtc,"gIBSCBS"); E(group,"vBC",f"{item_total:.2f}")
            state=E(group,"gIBSUF"); E(state,"pIBSUF",f"{q(p.ibs_state_rate,'0.0000'):.4f}"); E(state,"vIBSUF",f"{q(item_total*p.ibs_state_rate/100):.2f}")
            city=E(group,"gIBSMun"); E(city,"pIBSMun",f"{q(p.ibs_city_rate,'0.0000'):.4f}"); E(city,"vIBSMun",f"{q(item_total*p.ibs_city_rate/100):.2f}"); E(group,"vIBS",f"{q(item_total*(p.ibs_state_rate+p.ibs_city_rate)/100):.2f}")
            cbs=E(group,"gCBS"); E(cbs,"pCBS",f"{q(p.cbs_rate,'0.0000'):.4f}"); E(cbs,"vCBS",f"{q(item_total*p.cbs_rate/100):.2f}")
    discount=q(cart.discount); icmstot=E(E(inf,"total"),"ICMSTot")
    totals={"vBC":total_products if total_tax else 0,"vICMS":total_tax,"vICMSDeson":0,"vFCP":0,"vBCST":0,"vST":0,"vFCPST":0,"vFCPSTRet":0,"vProd":total_products,"vFrete":0,"vSeg":0,"vDesc":discount,"vII":0,"vIPI":0,"vIPIDevol":0,"vPIS":0,"vCOFINS":0,"vOutro":0,"vNF":q(total_products-discount),"vTotTrib":total_tax}
    for tag,val in totals.items():E(icmstot,tag,f"{q(val):.2f}")
    E(E(inf,"transp"),"modFrete","9"); pag=E(inf,"pag"); detpag=E(pag,"detPag"); E(detpag,"indPag","0"); E(detpag,"tPag",PAYMENTS.get(payment,"99")); E(detpag,"vPag",f"{q(cart.total):.2f}")
    return root,key,number

def add_supplement(root,key,config,emission_type="1",digest_value=""):
    base=f"{key}|3|{config['nfce_csc_id']}|{config['nfce_csc']}"
    token=hashlib.sha1(base.encode()).hexdigest().upper()
    query=f"p={key}|3|{config['nfce_csc_id']}|{token}"
    url=config["nfce_qrcode_url"].rstrip("?")+"?"+query
    supp=E(root,"infNFeSupl"); E(supp,"qrCode",url); E(supp,"urlChave",config["nfce_consult_url"])
    return url

def serialize(root): return etree.tostring(root,encoding="utf-8",xml_declaration=True,pretty_print=False)
