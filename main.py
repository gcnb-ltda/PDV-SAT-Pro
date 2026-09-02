import sys
from pathlib import Path
from dotenv import load_dotenv
from qt_compat import QApplication

load_dotenv(Path(__file__).with_name(".env"))
from database import init_db
from fiscal import create_fiscal
from ui import MainWindow

def main():
    init_db(); app=QApplication(sys.argv); app.setApplicationName("PDV SAT Pro")
    window=MainWindow(create_fiscal()); window.show(); return app.exec()

if __name__ == "__main__": raise SystemExit(main())
