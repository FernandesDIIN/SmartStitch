import os
from natsort import natsorted
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QAbstractItemView, QDialog, QDialogButtonBox, QFileDialog, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout)

LABELS = {
 'pt': {'queue':'Fila de pastas', 'add':'Adicionar pasta', 'choose':'Marcar subpastas', 'remove':'Remover selecionadas', 'clear':'Limpar fila', 'hint':'Pastas são processadas separadamente, na ordem da lista. Se a fila não estiver vazia, ela terá prioridade sobre a pasta principal.', 'parent':'Escolha a pasta que contém os capítulos', 'select':'Marque as pastas que deseja adicionar', 'all':'Marcar todas', 'none':'Desmarcar todas', 'empty':'Nenhuma subpasta encontrada.', 'overlap':'Esta pasta já está na fila ou contém outra pasta que está na fila.', 'open':'Escolha uma pasta', 'done':'Pronto', 'button':'Fila de pastas'},
 'en': {'queue':'Folder queue', 'add':'Add folder', 'choose':'Select subfolders', 'remove':'Remove selected', 'clear':'Clear queue', 'hint':'Folders are processed separately, in the order shown. A non-empty queue takes priority over the main input folder.', 'parent':'Choose the folder containing the chapters', 'select':'Select the folders to add', 'all':'Select all', 'none':'Clear selection', 'empty':'No subfolders found.', 'overlap':'This folder is already queued or overlaps another queued folder.', 'open':'Choose a folder', 'done':'Done', 'button':'Folder queue'},
 'es': {'queue':'Cola de carpetas', 'add':'Añadir carpeta', 'choose':'Marcar subcarpetas', 'remove':'Quitar seleccionadas', 'clear':'Vaciar cola', 'hint':'Las carpetas se procesan por separado, en el orden indicado. Si la cola no está vacía, tiene prioridad sobre la carpeta principal.', 'parent':'Elige la carpeta que contiene los capítulos', 'select':'Marca las carpetas que deseas añadir', 'all':'Marcar todas', 'none':'Desmarcar todas', 'empty':'No hay subcarpetas.', 'overlap':'Esta carpeta ya está en la cola o contiene otra carpeta de la cola.', 'open':'Elige una carpeta', 'done':'Listo', 'button':'Cola de carpetas'}}

class QueueDialog(QDialog):
    def __init__(self, parent, paths, language):
        super().__init__(parent)
        self.t = LABELS[language]; self.setWindowTitle(self.t['queue']); self.resize(700, 400)
        layout = QVBoxLayout(self); hint = QLabel(self.t['hint']); hint.setWordWrap(True); layout.addWidget(hint)
        self.list = QListWidget(); self.list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection); self.list.addItems(paths); layout.addWidget(self.list)
        row = QHBoxLayout()
        for label, callback in [('add', self.add_one), ('choose', self.choose_many), ('remove', self.remove), ('clear', self.list.clear)]:
            button = QPushButton(self.t[label]); button.clicked.connect(callback); row.addWidget(button)
        layout.addLayout(row); done = QPushButton(self.t['done']); done.clicked.connect(self.accept); layout.addWidget(done)
    def paths(self):
        return [self.list.item(i).text() for i in range(self.list.count())]
    def append_path(self, path):
        path = os.path.abspath(path); norm = os.path.normcase(os.path.realpath(path))
        for current in self.paths():
            old = os.path.normcase(os.path.realpath(current))
            try: common = os.path.commonpath([norm, old])
            except ValueError: continue
            if common in (norm, old): return False
        self.list.addItem(path); return True
    def add_one(self):
        path = QFileDialog.getExistingDirectory(self, self.t['open'])
        if path and not self.append_path(path): QMessageBox.information(self, 'SmartStitch', self.t['overlap'])
    def choose_many(self):
        parent = QFileDialog.getExistingDirectory(self, self.t['parent'])
        if not parent: return
        try:
            paths = [os.path.join(parent, name) for name in natsorted(os.listdir(parent)) if os.path.isdir(os.path.join(parent, name)) and not name.endswith(' [stitched]')]
        except OSError as error:
            QMessageBox.warning(self, 'SmartStitch', str(error)); return
        if not paths: QMessageBox.information(self, 'SmartStitch', self.t['empty']); return
        dialog = QDialog(self); dialog.setWindowTitle(self.t['select']); dialog.resize(480, 420)
        layout = QVBoxLayout(dialog); layout.addWidget(QLabel(self.t['select'])); listing = QListWidget(); layout.addWidget(listing)
        for path in paths:
            item = QListWidgetItem(os.path.basename(path)); item.setData(Qt.ItemDataRole.UserRole, path); item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable); item.setCheckState(Qt.CheckState.Unchecked); listing.addItem(item)
        row = QHBoxLayout()
        for text, state in ((self.t['all'], Qt.CheckState.Checked), (self.t['none'], Qt.CheckState.Unchecked)):
            button = QPushButton(text); button.clicked.connect(lambda checked=False, state=state: [listing.item(i).setCheckState(state) for i in range(listing.count())]); row.addWidget(button)
        layout.addLayout(row); buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel); buttons.accepted.connect(dialog.accept); buttons.rejected.connect(dialog.reject); layout.addWidget(buttons)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            skipped = False
            for i in range(listing.count()):
                item = listing.item(i)
                if item.checkState() == Qt.CheckState.Checked and not self.append_path(item.data(Qt.ItemDataRole.UserRole)): skipped = True
            if skipped: QMessageBox.information(self, 'SmartStitch', self.t['overlap'])
    def remove(self):
        for item in self.list.selectedItems(): self.list.takeItem(self.list.row(item))
