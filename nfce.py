from __future__ import annotations
import base64, hashlib, json, uuid
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
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
    def status(self): return "NFC-e REAL — CONECTOR PENDENTE DE PROVEDOR FISCAL"
    def authorize(self, cart, payment, customer_document=""):
        raise RuntimeError("Configure o provedor NFC-e homologado no adaptador NfceSefaz.")

PAYMENT_CODES={"Dinheiro":"01","Cartão de crédito":"03","Cartão de débito":"04","PIX":"17"}

def focus_payload(cart,payment,customer_document,config):
    missing=[]
    items=[]; discount_left=cart.discount
    for number,item in enumerate(cart.items,1):
        product=item.product
        for field,label in ((product.ncm,"NCM"),(product.cfop,"CFOP"),(product.origin,"origem ICMS"),(product.icms_cst,"CST/CSOSN ICMS"),(product.pis_cst,"CST PIS"),(product.cofins_cst,"CST COFINS")):
            if not str(field).strip(): missing.append(f"{product.name}: {label}")
        gross=item.total
        allocated=(cart.discount*gross/cart.subtotal).quantize(Decimal("0.01"),rounding=ROUND_HALF_UP) if cart.subtotal else Decimal("0")
        if number==len(cart.items): allocated=discount_left
        discount_left-=allocated; taxable=gross-allocated
        data={"numero_item":number,"codigo_produto":str(product.id),"descricao":product.name[:120],"codigo_ncm":product.ncm,"cfop":product.cfop,"unidade_comercial":product.unit,"quantidade_comercial":float(item.quantity),"valor_unitario_comercial":float(product.price),"valor_bruto":float(gross),"valor_desconto":float(allocated),"unidade_tributavel":product.unit,"quantidade_tributavel":float(item.quantity),"valor_unitario_tributavel":float(product.price),"icms_origem":product.origin,"icms_situacao_tributaria":product.icms_cst,"pis_situacao_tributaria":product.pis_cst,"cofins_situacao_tributaria":product.cofins_cst}
        if product.barcode.isdigit() and len(product.barcode) in (8,12,13,14): data["codigo_barras_comercial"]=product.barcode
        if product.cest: data["cest"]=product.cest
        if Decimal(str(product.icms_rate or 0))>0: data.update(icms_modalidade_base_calculo="3",icms_base_calculo=float(taxable),icms_aliquota=float(product.icms_rate),icms_valor=float((taxable*Decimal(str(product.icms_rate))/100).quantize(Decimal("0.01"))))
        if Decimal(str(product.pis_rate or 0))>0: data.update(pis_base_calculo=float(taxable),pis_aliquota_porcentual=float(product.pis_rate),pis_valor=float((taxable*Decimal(str(product.pis_rate))/100).quantize(Decimal("0.01"))))
        if Decimal(str(product.cofins_rate or 0))>0: data.update(cofins_base_calculo=float(taxable),cofins_aliquota_porcentual=float(product.cofins_rate),cofins_valor=float((taxable*Decimal(str(product.cofins_rate))/100).quantize(Decimal("0.01"))))
        items.append(data)
    if missing: raise ValueError("Cadastro fiscal incompleto:\n"+"\n".join(missing))
    payload={"cnpj_emitente":"".join(filter(str.isdigit,config.get("cnpj",""))),"data_emissao":datetime.now().astimezone().isoformat(timespec="seconds"),"natureza_operacao":"VENDA AO CONSUMIDOR","tipo_documento":"1","local_destino":"1","finalidade_emissao":"1","consumidor_final":"1","presenca_comprador":"1","modalidade_frete":"9","regime_tributario_emitente":config.get("tax_regime","3"),"items":items,"formas_pagamento":[{"indicador_pagamento":"0","forma_pagamento":PAYMENT_CODES.get(payment,"99"),"valor_pagamento":float(cart.total)}]}
    if customer_document: payload["cpf_destinatario" if len(customer_document)==11 else "cnpj_destinatario"]=customer_document; payload["indicador_inscricao_estadual_destinatario"]="9"
    return payload

class FocusNfce:
    def __init__(self,config): self.config=config
    def status(self): return f"NFC-e FOCUS NFE — {self.config.get('environment','homologacao').upper()}"
    def authorize(self,cart,payment,customer_document=""):
        token=self.config.get("focus_token","")
        if not token: raise RuntimeError("Informe o token Focus NFe na configuração fiscal.")
        base="https://api.focusnfe.com.br" if self.config.get("environment")=="producao" else "https://homologacao.focusnfe.com.br"
        reference=f"PDV-{datetime.now():%Y%m%d%H%M%S}-{uuid.uuid4().hex[:10]}"
        url=base+"/v2/nfce?"+urlencode({"ref":reference,"completa":1}); body=json.dumps(focus_payload(cart,payment,customer_document,self.config)).encode("utf-8"); authorization=base64.b64encode((token+":").encode()).decode()
        request=Request(url,data=body,method="POST",headers={"Authorization":"Basic "+authorization,"Accept":"application/json","Content-Type":"application/json"})
        try:
            with urlopen(request,timeout=45) as response: status_code=response.status; data=json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            status_code=exc.code
            try: data=json.loads(exc.read().decode("utf-8"))
            except Exception: data={"mensagem":str(exc)}
        except URLError as exc: raise RuntimeError(f"Falha de comunicação com a Focus NFe: {exc.reason}") from exc
        except (ValueError,UnicodeDecodeError) as exc: raise RuntimeError("O provedor fiscal retornou uma resposta inválida.") from exc
        status=str(data.get("status","")).lower(); ok=status_code==201 and status in ("autorizado","autorizada")
        key=str(data.get("chave_nfe") or data.get("chave_nfce") or "")
        if not ok:
            message=data.get("mensagem_sefaz") or data.get("mensagem") or data.get("erro") or json.dumps(data,ensure_ascii=False)
            return FiscalResult(False,key,f"HTTP {status_code} | {message}")
        return FiscalResult(True,key,json.dumps(data,ensure_ascii=False))

def create_nfce(config):
    if config.get("nfce_provider")=="Focus NFe":
        return FocusNfce(config) if config.get("focus_token") else NfceSimulator(config)
    return NfceSefaz(config) if config.get("environment") == "producao" else NfceSimulator(config)
