try:
    from PySide6.QtCore import Qt, QDate
    from PySide6.QtGui import QKeySequence, QShortcut
    from PySide6.QtWidgets import *
    QT_VERSION = 6
except ImportError:
    from PySide2.QtCore import Qt, QDate
    from PySide2.QtGui import QKeySequence
    from PySide2.QtWidgets import *
    QShortcut = QShortcut
    QT_VERSION = 5

def dialog_exec(dialog):
    return dialog.exec() if QT_VERSION == 6 else dialog.exec_()
