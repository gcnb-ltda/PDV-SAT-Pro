import sys
from pathlib import Path
from dotenv import load_dotenv
from qt_compat import QApplication, application_exec

load_dotenv(Path(__file__).with_name(".env"))
from database import init_db
from fiscal import create_fiscal
from ui import MainWindow
from audit import logger
from report_scheduler import run_due_schedules

def main():
    init_db(); logger.info("Aplicação iniciada")
    try:
        for path in run_due_schedules(): logger.info("Relatório agendado criado: %s",Path(path).name)
    except Exception: logger.exception("Falha ao executar relatórios agendados")
    app=QApplication(sys.argv); app.setApplicationName("PDV SAT Pro")
    window=MainWindow(create_fiscal()); window.show(); return application_exec(app)

if __name__ == "__main__": raise SystemExit(main())
