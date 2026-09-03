from datetime import datetime
from pathlib import Path
import shutil
from database import database_file

def create_backup(destination):
    target=Path(destination)/f"pdv-backup-{datetime.now():%Y%m%d-%H%M%S}.db"
    shutil.copy2(database_file(),target); return target

def restore_backup(source):
    source=Path(source)
    if not source.is_file(): raise ValueError("Arquivo de backup inválido.")
    if source.read_bytes()[:16] != b"SQLite format 3\x00": raise ValueError("O arquivo não é um banco SQLite válido.")
    current=database_file(); safety=current.with_suffix(".before-restore.db")
    if current.exists(): shutil.copy2(current,safety)
    shutil.copy2(source,current); return safety
