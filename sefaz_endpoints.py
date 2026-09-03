"""Catálogo versionado de autorizadores NFC-e e serviços SEFAZ.

Os endereços podem mudar por ato de cada UF. O catálogo embutido é um snapshot e
todo serviço aceita override em ``sefaz_endpoints_json`` para atualização sem
recompilar o PDV. Nunca faça fallback silencioso para um autorizador diferente.
"""
from __future__ import annotations
import json

UF_CODES = {"RO":"11","AC":"12","AM":"13","RR":"14","PA":"15","AP":"16","TO":"17","MA":"21","PI":"22","CE":"23","RN":"24","PB":"25","PE":"26","AL":"27","SE":"28","BA":"29","MG":"31","ES":"32","RJ":"33","SP":"35","PR":"41","SC":"42","RS":"43","MS":"50","MT":"51","GO":"52","DF":"53"}

# Relação de autorizadores publicada pelo Portal Nacional. Endpoints estaduais
# que não seguem um padrão ficam em override obrigatório (fail closed).
AUTHORIZER = {
    **{uf:"SVRS" for uf in ("AC","AL","AP","CE","DF","ES","MA","PA","PB","PI","RJ","RN","RO","RR","RS","SC","SE","TO")},
    "AM":"AM", "BA":"BA", "GO":"GO", "MG":"MG", "MS":"MS", "MT":"MT",
    "PE":"PE", "PR":"PR", "SP":"SP",
}

_BASE = {
    "SVRS": {"homologacao":"https://nfce-homologacao.svrs.rs.gov.br/ws", "producao":"https://nfce.svrs.rs.gov.br/ws"},
    "SP": {"homologacao":"https://homologacao.nfce.fazenda.sp.gov.br/ws", "producao":"https://nfce.fazenda.sp.gov.br/ws"},
}
_PATHS = {
    "status":"NFeStatusServico/NFeStatusServico4.asmx",
    "authorization":"NfeAutorizacao/NFeAutorizacao4.asmx",
    "receipt":"NFeRetAutorizacao/NFeRetAutorizacao4.asmx",
    "event":"NFeRecepcaoEvento/NFeRecepcaoEvento4.asmx",
    "inutilization":"NFeInutilizacao/NFeInutilizacao4.asmx",
}

def endpoint(uf: str, environment: str, service: str, overrides: str | dict | None = None) -> str:
    uf, environment = uf.upper(), environment.lower()
    if uf not in AUTHORIZER or environment not in ("homologacao", "producao") or service not in _PATHS:
        raise ValueError("UF, ambiente ou serviço SEFAZ inválido.")
    custom = json.loads(overrides) if isinstance(overrides, str) and overrides.strip() else (overrides or {})
    value = custom.get(uf, {}).get(environment, {}).get(service)
    if value:
        if not value.startswith("https://"):
            raise ValueError("Endpoint SEFAZ deve usar HTTPS.")
        return value
    authorizer = AUTHORIZER[uf]
    if authorizer not in _BASE:
        raise RuntimeError(f"Endpoint de {uf}/{authorizer} requer atualização oficial no campo de overrides.")
    return f"{_BASE[authorizer][environment]}/{_PATHS[service]}"

def ibge_uf_code(uf: str) -> str:
    try: return UF_CODES[uf.upper()]
    except KeyError as exc: raise ValueError("UF brasileira inválida.") from exc
