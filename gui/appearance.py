from PySide6.QtCore import QSettings, Qt, QTimer
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication, QComboBox, QHBoxLayout, QWidget

TEXT = {
'en': ['Language','Appearance','System','Light','Dark','Basic','Advanced','Post-process','Input and output','Input folder','Browse','Output folder','Output settings','Output format','Image quality [1–100%]','Approximate page height','Width adjustment','Custom width [pixels]','Cut detection','Detector','Direct slicing','Safe bands (smart)','Profiles','Current profile','Add','Delete','Profile name','Post-processing','Run post-processing after completion','Application path','Arguments','Status','Start processing','No adjustment','Automatic uniform width','Custom width','Ready','Select input folder','Select post-processing application','Choose a folder before starting.','Cannot delete the last profile.'],
'pt': ['Idioma','Aparência','Sistema','Claro','Escuro','Básico','Avançado','Pós-processamento','Entrada e saída','Pasta das imagens','Procurar','Pasta de saída','Configurações de saída','Formato de saída','Qualidade da imagem [1–100%]','Altura aproximada da página','Ajuste de largura','Largura personalizada [pixels]','Detecção de corte','Detector','Corte direto','Faixas seguras (inteligente)','Perfis','Perfil atual','Adicionar','Excluir','Nome do perfil','Pós-processamento','Executar pós-processamento ao terminar','Caminho do aplicativo','Argumentos','Estado','Iniciar processamento','Sem ajuste','Largura uniforme automática','Largura personalizada','Pronto','Selecionar pasta de imagens','Selecionar aplicativo de pós-processamento','Escolha uma pasta antes de iniciar.','Não é possível excluir o último perfil.'],
'es': ['Idioma','Apariencia','Sistema','Claro','Oscuro','Básico','Avanzado','Posprocesamiento','Entrada y salida','Carpeta de imágenes','Buscar','Carpeta de salida','Configuración de salida','Formato de salida','Calidad de imagen [1–100%]','Altura aproximada de página','Ajuste de anchura','Anchura personalizada [píxeles]','Detección de corte','Detector','Corte directo','Franjas seguras (inteligente)','Perfiles','Perfil actual','Añadir','Eliminar','Nombre del perfil','Posprocesamiento','Ejecutar posprocesamiento al terminar','Ruta de la aplicación','Argumentos','Estado','Iniciar procesamiento','Sin ajuste','Anchura uniforme automática','Anchura personalizada','Listo','Seleccionar carpeta de imágenes','Seleccionar aplicación de posprocesamiento','Elige una carpeta antes de empezar.','No se puede eliminar el último perfil.']}

class Appearance:
    def __init__(self, window):
        self.window = window
        self.prefs = QSettings('SmartStitch', 'SmartStitchSafeCuts')
        self.language = self.prefs.value('language', 'en')
        if self.language not in TEXT: self.language = 'en'
        self.theme = self.prefs.value('theme', 'system')
        self._system_dark = QApplication.instance().palette().color(QPalette.ColorRole.Window).lightness() < 128
        self._last_system_dark = None
        self.controls = QWidget(window.mainTabWidget)
        self.controls.setObjectName('appearanceControls')
        row = QHBoxLayout(self.controls)
        row.setContentsMargins(4, 0, 0, 0)
        row.setSpacing(6)
        self.language_box = QComboBox()
        for title, code in [('English','en'),('Português','pt'),('Español','es')]:
            self.language_box.addItem(title, code)
        self.theme_box = QComboBox()
        for code in ('system','light','dark'):
            self.theme_box.addItem('', code)
        row.addWidget(self.language_box)
        row.addWidget(self.theme_box)
        window.mainTabWidget.setCornerWidget(self.controls, Qt.Corner.TopRightCorner)
        self.language_box.setCurrentIndex(max(0,self.language_box.findData(self.language)))
        self.theme_box.setCurrentIndex(max(0,self.theme_box.findData(self.theme)))
        self.language_box.currentIndexChanged.connect(self.change_language); self.theme_box.currentIndexChanged.connect(self.change_theme)
        hints = QApplication.styleHints()
        if hasattr(hints,'colorSchemeChanged'): hints.colorSchemeChanged.connect(self.system_changed)
        self.timer = QTimer(window); self.timer.timeout.connect(self.check_system_theme); self.timer.start(2000)
        self.translate(); self.apply_theme()
    def tr(self, index): return TEXT[self.language][index]
    def change_language(self):
        self.language = self.language_box.currentData(); self.prefs.setValue('language',self.language); self.translate()
    def change_theme(self):
        self.theme = self.theme_box.currentData(); self.prefs.setValue('theme',self.theme); self.apply_theme()
    def windows_dark(self):
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                return not bool(winreg.QueryValueEx(key, "AppsUseLightTheme")[0])
        except (ImportError, OSError):
            hints = QApplication.styleHints()
            if hasattr(hints, "colorScheme") and hints.colorScheme() != Qt.ColorScheme.Unknown:
                return hints.colorScheme() == Qt.ColorScheme.Dark
            return self._system_dark
    def check_system_theme(self):
        if self.theme == "system" and self.windows_dark() != self._last_system_dark:
            self.apply_theme()
    def system_changed(self, *_):
        if self.theme == 'system': self.apply_theme()
    def translate(self):
        w,t = self.window,self.tr
        self.language_box.setToolTip(t(0)); self.theme_box.setToolTip(t(1))
        for i in range(3): self.theme_box.setItemText(i,t(2+i))
        for i in range(3): w.mainTabWidget.setTabText(i,t(5+i))
        for name,idx in {'browseGroupBox':8,'generalGroupBox':12,'detectorGroupBox':18,'profileGroupBox':22,'postProcessGroupBox':27,'ActionGroupBox':31}.items(): getattr(w,name).setTitle(t(idx))
        for name,idx in {'inputLabel':9,'browseButton':10,'outputLabel':11,'outputTypeLabel':13,'lossyLabel':14,'heightLabel':15,'widthEnforcementLabel':16,'customWidthLabel':17,'label':19,'currentProfileLabel':23,'addProfileButton':24,'removeProfileButton':25,'currentProfileNameLabel':26,'runProcessCheckbox':28,'postProcessAppLabel':29,'browsePostProcessAppButton':10,'postProcessArgsLabel':30,'startProcessButton':32}.items(): getattr(w,name).setText(t(idx))
        for box,values in ((w.detectorTypeDropdown,(21,)),(w.widthEnforcementDropdown,(33,34,35))):
            box.blockSignals(True)
            for i,value in enumerate(values): box.setItemText(i,t(value))
            box.blockSignals(False)
        if not getattr(w,'_processing',False): w.statusField.setText(t(36))
    def apply_theme(self):
        app=QApplication.instance(); dark=self.theme=='dark'
        if self.theme=='system':
            dark = self.windows_dark()
            self._last_system_dark = dark
        bg,panel,field,fg,muted,border=(('#101622','#192231','#202c3d','#edf3fa','#aebed1','#34465d') if dark else ('#f2f5f9','#ffffff','#f8fafc','#1a2738','#53677e','#d3dce7'))
        app.setStyleSheet(f'''
        QWidget {{ background:{bg}; color:{fg}; font-family:"Segoe UI"; font-size:10pt; }}
        #appearanceControls {{ background:transparent; }} #appearanceControls QComboBox {{ padding:4px 5px; }}
        QGroupBox {{ background:{panel}; border:1px solid {border}; border-radius:10px; margin-top:14px; padding:13px 12px 10px; font-weight:600; }} QGroupBox::title {{ subcontrol-origin:margin; left:12px; padding:0 5px; }} QGroupBox QLabel {{ background:transparent; }}
        QLineEdit,QSpinBox,QComboBox,QTextEdit,QPlainTextEdit {{ background:{field}; border:1px solid {border}; border-radius:6px; padding:5px 8px; color:{fg}; selection-background-color:#258b61; }} QComboBox QAbstractItemView {{ background:{panel}; color:{fg}; selection-background-color:#258b61; }}
        QPushButton {{ background:#26c889; color:#153d2c; border:none; border-radius:6px; padding:7px 14px; font-weight:600; }} QPushButton:hover {{ background:#20ae75; }} QPushButton:disabled {{ background:{border}; color:{muted}; }}
        QTabWidget::pane {{ border:none; }} QTabBar::tab {{ background:transparent; color:{muted}; padding:9px 10px; border-bottom:3px solid transparent; }} QTabBar::tab:selected {{ color:{fg}; border-bottom:3px solid #26c889; font-weight:600; }}
        QProgressBar {{ background:{field}; border:1px solid {border}; border-radius:5px; text-align:center; }} QProgressBar::chunk {{ background:#26c889; border-radius:4px; }}
        QCheckBox::indicator {{ width:16px; height:16px; border:1px solid {border}; border-radius:3px; background:{field}; }} QCheckBox::indicator:checked {{ background:#26c889; border:1px solid #26c889; }}
        ''')
