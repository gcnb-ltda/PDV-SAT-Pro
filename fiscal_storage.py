from __future__ import annotations
import json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from platformdirs import user_data_dir

ROOT=Path(user_data_dir("PDV-SAT-Pro","GCNB"))/"fiscal"

def _atomic(path:Path,data:bytes):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,temp=tempfile.mkstemp(dir=path.parent,prefix=path.name+".",suffix=".tmp")
    try:
        with os.fdopen(fd,"wb") as stream: stream.write(data); stream.flush(); os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if os.path.exists(temp): os.unlink(temp)

def save_document(kind:str,key:str,xml:bytes,metadata:dict|None=None,root:Path=ROOT):
    now=datetime.now(timezone.utc); folder=root/kind/now.strftime("%Y/%m")
    xml_path=folder/f"{key}.xml"; meta_path=folder/f"{key}.json"
    _atomic(xml_path,xml); _atomic(meta_path,json.dumps({"saved_at":now.isoformat(),**(metadata or {})},ensure_ascii=False,indent=2).encode())
    return xml_path

def enqueue(key:str,xml:bytes,metadata:dict|None=None,root:Path=ROOT): return save_document("contingency/pending",key,xml,metadata,root)

def pending(root:Path=ROOT): return sorted((root/"contingency/pending").rglob("*.xml")) if (root/"contingency/pending").exists() else []
