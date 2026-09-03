from __future__ import annotations
from pathlib import Path
from lxml import etree

SCHEMA_DIR=Path(__file__).with_name("schemas")

def validate_xml(xml, schema_name: str, schema_dir: Path | str = SCHEMA_DIR):
    path=Path(schema_dir or SCHEMA_DIR)/schema_name
    if not path.is_file():
        raise RuntimeError(f"Schema oficial ausente: {path}. Instale o pacote PL_NFe vigente antes da homologação.")
    try: document=etree.fromstring(xml if isinstance(xml,bytes) else xml.encode())
    except etree.XMLSyntaxError as exc: raise ValueError(f"XML malformado: {exc}") from exc
    schema=etree.XMLSchema(etree.parse(str(path)))
    if not schema.validate(document):
        error=schema.error_log.last_error
        raise ValueError(f"XML rejeitado pelo XSD {schema_name}: linha {error.line}: {error.message}")
    return True
