import logging
from logging.handlers import RotatingFileHandler
from platformdirs import user_log_dir
from pathlib import Path

SENSITIVE = ("password", "senha", "sat_code", "csc", "certificate")

class RedactFilter(logging.Filter):
    def filter(self, record):
        text=str(record.msg)
        for word in SENSITIVE:
            if word in text.lower(): record.msg="Evento sensível omitido"; record.args=(); break
        return True

def configure_logging():
    folder=Path(user_log_dir("PDV-SAT-Pro","GCNB")); folder.mkdir(parents=True,exist_ok=True)
    handler=RotatingFileHandler(folder/"pdv.log",maxBytes=1_000_000,backupCount=5,encoding="utf-8")
    handler.addFilter(RedactFilter()); handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger=logging.getLogger("pdv"); logger.setLevel(logging.INFO); logger.addHandler(handler); return logger

logger=configure_logging()
