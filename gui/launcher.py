from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from .controller import initialize_gui


def launch():
    app = QApplication([])
    app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)
    initialize_gui()
    app.exec()
