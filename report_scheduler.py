from __future__ import annotations
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from platformdirs import user_config_dir
from reports import generate_report, export_report, REPORTS

SCHEDULE_FILE=Path(user_config_dir("PDV-SAT-Pro","GCNB"))/"report_schedules.json"

def load_schedules():
    try: return json.loads(SCHEDULE_FILE.read_text(encoding="utf-8"))
    except (FileNotFoundError,json.JSONDecodeError): return []

def save_schedules(items):
    SCHEDULE_FILE.parent.mkdir(parents=True,exist_ok=True)
    SCHEDULE_FILE.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding="utf-8")

def add_schedule(kind,frequency,folder,format_name="xlsx"):
    if kind not in REPORTS: raise ValueError("Relatório desconhecido.")
    if frequency not in ("Diário","Semanal","Mensal"): raise ValueError("Frequência inválida.")
    if not Path(folder).is_dir(): raise ValueError("Selecione uma pasta válida.")
    items=load_schedules(); items.append({"kind":kind,"frequency":frequency,"folder":folder,"format":format_name,"next_run":date.today().isoformat(),"active":True}); save_schedules(items)

def delete_schedule(index):
    items=load_schedules()
    if 0 <= index < len(items): items.pop(index); save_schedules(items)

def run_due_schedules(today=None):
    today=today or date.today(); items=load_schedules(); created=[]
    for item in items:
        if not item.get("active",True) or date.fromisoformat(item["next_run"]) > today: continue
        days=1 if item["frequency"]=="Diário" else 7 if item["frequency"]=="Semanal" else 30
        report=generate_report(item["kind"],today-timedelta(days=days-1),today)
        filename=f"{item['kind']}-{today:%Y%m%d}.{item.get('format','xlsx')}"
        created.append(str(export_report(report,str(Path(item["folder"])/filename))))
        item["next_run"]=(today+timedelta(days=days)).isoformat()
    save_schedules(items); return created
