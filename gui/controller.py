import os

from PySide6.QtCore import QThread, Signal
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from assets.SmartStitchLogo import icon
from core.services import SettingsHandler
from core.utils.constants import OUTPUT_SUFFIX
from gui.process import GuiStitchProcess
from gui.appearance import Appearance
from core.utils.errors import WebPSizeError

SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class ProcessThread(QThread):
    progress = Signal(int, str)
    postProcessConsole = Signal(str)
    webpError = Signal(str)
    forcedCuts = Signal(object)

    def __init__(self, parent):
        super(ProcessThread, self).__init__(parent)

    def run(self):
        process = GuiStitchProcess()
        try:
            process.run_with_error_msgs(
                input_path=MainWindow.inputField.text(),
                output_path=MainWindow.outputField.text(),
                status_func=self.progress.emit,
                console_func=self.postProcessConsole.emit,
                forced_cut_func=self.forcedCuts.emit,
            )
        except WebPSizeError as error:
            self.webpError.emit(str(error))
        except Exception:
            pass



def initialize_gui():
    global MainWindow
    global settings
    global appVersion
    global appAuthor
    global processThread
    global appearance
    MainWindow = QUiLoader().load(os.path.join(SCRIPT_DIRECTORY, 'layout.ui'))
    settings = SettingsHandler()
    MainWindow.detectorTypeDropdown.removeItem(0)
    # Sets Window Title & Icon
    pixmap = QPixmap()
    pixmap.loadFromData(icon)
    appIcon = QIcon(pixmap)
    MainWindow.setWindowIcon(appIcon)
    # Sets Window Title
    appVersion = "3.1"
    appAuthor = "MechTechnology"
    MainWindow.setWindowTitle("SmartStitch")
    # Controls Setup
    on_load()
    bind_signals()
    appearance = Appearance(MainWindow)
    MainWindow.addProfileButton.setMaximumSize(16777215, 16777215)
    MainWindow.removeProfileButton.setMaximumSize(16777215, 16777215)
    MainWindow.resize(600, 625)
    # Sets up process thread
    processThread = ProcessThread(MainWindow)
    processThread.progress.connect(update_process_progress)
    processThread.postProcessConsole.connect(update_postprocess_console)
    processThread.finished.connect(process_finished)
    processThread.webpError.connect(show_webp_error)
    processThread.forcedCuts.connect(show_forced_cuts)
    # Show Window
    MainWindow.show()


def on_load(load_profiles=True):
    # App Fields
    MainWindow.statusField.setText("Idle")
    MainWindow.statusProgressBar.setValue(0)
    # Settings Fields
    MainWindow.outputTypeDropdown.setCurrentText(settings.load("output_type"))
    MainWindow.lossyField.setValue(settings.load("lossy_quality"))
    MainWindow.heightField.setValue(settings.load("split_height"))
    MainWindow.widthEnforcementDropdown.setCurrentIndex(settings.load("enforce_type"))
    MainWindow.customWidthField.setValue(settings.load("enforce_width"))
    MainWindow.detectorTypeDropdown.setCurrentIndex(0)
    MainWindow.detectorSensitivityField.setValue(settings.load("senstivity"))
    MainWindow.scanStepField.setValue(settings.load("scan_step"))
    MainWindow.ignoreMarginField.setValue(settings.load("ignorable_pixels"))
    MainWindow.runProcessCheckbox.setChecked(settings.load("run_postprocess"))
    MainWindow.postProcessAppField.setText(settings.load("postprocess_app"))
    MainWindow.postProcessArgsField.setText(settings.load("postprocess_args"))
    output_type_changed(False)
    enforce_type_changed(False)
    detector_type_changed(False)
    if load_profiles:
        update_profiles_list()
        MainWindow.currentProfileDropdown.setCurrentIndex(settings.get_current_index())
        current_profile_changed(False)


def bind_signals():
    MainWindow.inputField.textChanged.connect(input_field_changed)
    MainWindow.browseButton.clicked.connect(browse_location)
    MainWindow.outputTypeDropdown.currentTextChanged.connect(output_type_changed)
    MainWindow.lossyField.valueChanged.connect(lossy_quality_changed)
    MainWindow.heightField.valueChanged.connect(split_height_changed)
    MainWindow.widthEnforcementDropdown.currentTextChanged.connect(enforce_type_changed)
    MainWindow.customWidthField.valueChanged.connect(custom_width_changed)
    MainWindow.detectorSensitivityField.valueChanged.connect(
        detector_sensitivity_changed
    )
    MainWindow.scanStepField.valueChanged.connect(scan_step_changed)
    MainWindow.ignoreMarginField.valueChanged.connect(ignorable_margin_changed)
    MainWindow.currentProfileDropdown.currentTextChanged.connect(
        current_profile_changed
    )
    MainWindow.currentProfileName.textChanged.connect(current_profile_name_changed)
    MainWindow.addProfileButton.clicked.connect(add_profile)
    MainWindow.removeProfileButton.clicked.connect(remove_profile)
    MainWindow.runProcessCheckbox.stateChanged.connect(run_postprocess_changed)
    MainWindow.browsePostProcessAppButton.clicked.connect(browse_postprocess_app)
    MainWindow.postProcessAppField.textChanged.connect(postprocess_app_changed)
    MainWindow.postProcessArgsField.textChanged.connect(postprocess_args_changed)
    MainWindow.startProcessButton.clicked.connect(launch_process_async)


def input_field_changed():
    input_path = MainWindow.inputField.text() or ""
    if input_path:
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)
    else:
        MainWindow.outputField.setText("")
    if (os.path.exists(input_path)):
        settings.save("last_browse_location", input_path)


def browse_location():
    start_directory = settings.load("last_browse_location")
    if not start_directory or not os.path.exists(start_directory):
        start_directory = os.path.expanduser("~")
    dialog = QFileDialog(
        MainWindow,
        appearance.tr(37),
        directory=start_directory,
        FileMode=QFileDialog.FileMode.Directory,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.inputField.setText(input_path)
        MainWindow.outputField.setText(input_path + OUTPUT_SUFFIX)


def output_type_changed(save=True):
    file_type = MainWindow.outputTypeDropdown.currentText()
    if save:
        settings.save("output_type", file_type)
    if file_type in ['.jpg', '.webp']:
        MainWindow.lossyWrapper.setHidden(False)
    else:
        MainWindow.lossyWrapper.setHidden(True)


def lossy_quality_changed():
    settings.save("lossy_quality", MainWindow.lossyField.value())


def split_height_changed():
    settings.save("split_height", MainWindow.heightField.value())


def enforce_type_changed(save=True):
    enforce_type = MainWindow.widthEnforcementDropdown.currentIndex()
    if save:
        settings.save("enforce_type", enforce_type)
    if enforce_type == 2:
        MainWindow.customWidthWrapper.setHidden(False)
    else:
        MainWindow.customWidthWrapper.setHidden(True)


def custom_width_changed():
    settings.save("enforce_width", MainWindow.customWidthField.value())


def detector_type_changed(save=True):
    # These options belonged to the former single-line detector.
    MainWindow.detectorSensitvityWrapper.hide()
    MainWindow.scanStepWrapper.hide()
    MainWindow.ignoreMarginWrapper.hide()


def detector_sensitivity_changed():
    settings.save("senstivity", MainWindow.detectorSensitivityField.value())


def scan_step_changed():
    settings.save("scan_step", MainWindow.scanStepField.value())


def ignorable_margin_changed():
    settings.save("ignorable_pixels", MainWindow.ignoreMarginField.value())


def update_profiles_list():
    profile_names = settings.get_profile_names()
    MainWindow.currentProfileDropdown.clear()
    for index in range(len(profile_names)):
        MainWindow.currentProfileDropdown.insertItem(index, profile_names[index])
    return len(profile_names)


def current_profile_changed(save=True):
    current_profile = MainWindow.currentProfileDropdown.currentIndex()
    if save:
        settings.set_current_index(current_profile)
        on_load(False)
    MainWindow.currentProfileName.setText(settings.get_current_profile_name())


def current_profile_name_changed():
    new_name = MainWindow.currentProfileName.text()
    settings.set_current_profile_name(new_name)
    current = MainWindow.currentProfileDropdown.currentIndex()
    MainWindow.currentProfileDropdown.setItemText(current, new_name)


def add_profile():
    profile_name = settings.add_profile()
    new_index = update_profiles_list() - 1
    MainWindow.currentProfileDropdown.setCurrentIndex(new_index)
    MainWindow.currentProfileName.setText(profile_name)


def remove_profile():
    current_profile = MainWindow.currentProfileDropdown.currentIndex()
    if len(settings.get_profile_names()) <= 1:
        QMessageBox.information(MainWindow, "SmartStitch", appearance.tr(40))
        return
    settings.remove_profile(current_profile)
    MainWindow.currentProfileDropdown.removeItem(current_profile)
    MainWindow.currentProfileDropdown.setCurrentIndex(0)


def run_postprocess_changed():
    settings.save("run_postprocess", MainWindow.runProcessCheckbox.isChecked())


def browse_postprocess_app():
    dialog = QFileDialog(
        MainWindow,
        appearance.tr(38),
        FileMode=QFileDialog.FileMode.ExistingFile,
    )
    if dialog.exec_() == QDialog.Accepted:
        input_path = dialog.selectedFiles()[0] or ""
        MainWindow.postProcessAppField.setText(input_path)


def postprocess_app_changed():
    settings.save("postprocess_app", MainWindow.postProcessAppField.text())


def postprocess_args_changed():
    settings.save("postprocess_args", MainWindow.postProcessArgsField.text())


def update_process_progress(percentage: int, message: str):
    MainWindow.statusField.setText(translate_status(message))
    MainWindow.statusProgressBar.setValue(percentage)

def update_postprocess_console(message: str):
    MainWindow.processConsoleField.append(message)


def launch_process_async():
    if not os.path.isdir(MainWindow.inputField.text()):
        QMessageBox.information(MainWindow, "SmartStitch", appearance.tr(39))
        return
    if processThread.isRunning():
        return
    MainWindow._processing = True
    MainWindow.startProcessButton.setEnabled(False)
    MainWindow.processConsoleField.clear()
    processThread.start()


def show_forced_cuts(report):
    messages = {
        'en': 'Some WebP pages required cuts without a safe blank band to stay below 16,000 px. A balloon or drawing may have been split. Please review these cuts:',
        'pt': 'Algumas páginas WebP precisaram ser cortadas sem uma faixa vazia segura para ficar abaixo de 16.000 px. Um balão ou desenho pode ter sido dividido. Revise estes cortes:',
        'es': 'Algunas páginas WebP necesitaron cortes sin una franja vacía segura para quedar por debajo de 16.000 px. Puede haberse dividido un globo o dibujo. Revisa estos cortes:',
    }
    details = []
    for folder, cuts in report:
        details.append(folder + ': ' + ', '.join(str(cut) + ' px' for cut in cuts))
    text = messages[appearance.language] + '\n\n' + '\n'.join(details)
    MainWindow.statusField.setText(messages[appearance.language])
    MainWindow.statusField.setToolTip(text)
    QMessageBox.warning(MainWindow, 'SmartStitch', text)


def show_webp_error(reason):
    messages = {
        'en': ('WebP is limited to 16,383 pixels per dimension. ',
               'The image is too wide. Reduce the output width or choose PNG.',
               'No safe cut was found within the WebP limit. Choose PNG to keep the longer page, or reduce the page height and try again.'),
        'pt': ('O formato WebP permite até 16.383 pixels por dimensão. ',
               'A imagem é larga demais. Reduza a largura de saída ou escolha PNG.',
               'Não foi encontrado um corte seguro dentro do limite do WebP. Escolha PNG para manter a página longa ou reduza a altura da página e tente novamente.'),
        'es': ('El formato WebP permite hasta 16.383 píxeles por dimensión. ',
               'La imagen es demasiado ancha. Reduce la anchura de salida o elige PNG.',
               'No se encontró un corte seguro dentro del límite de WebP. Elige PNG para conservar la página larga o reduce su altura y vuelve a intentarlo.'),
    }
    prefix, width, height = messages[appearance.language]
    text = prefix + (width if reason == 'width' else height)
    MainWindow.statusField.setText(text)
    MainWindow.statusField.setToolTip(text)
    QMessageBox.warning(MainWindow, 'SmartStitch', text)


def process_finished():
    MainWindow._processing = False
    MainWindow.startProcessButton.setEnabled(True)


def translate_status(message):
    if appearance.language == 'en':
        return message
    parts = {
        'pt': {
            'Idle - Process completed in': 'Concluído em', 'seconds': 'segundos',
            'WARNING: long pages; no nearby safe cut. Review output.': 'AVISO: páginas longas; não foi encontrado corte seguro próximo. Revise o resultado.',
            'Exploring input directory for working directories': 'Buscando pastas de imagens',
            'Working directories were found': 'pastas encontradas',
            'Preparing & loading images Into memory': 'Preparando e carregando imagens',
            'Combining images into a single combined image': 'Unindo imagens',
            'Detecting & selecting valid slicing points': 'Procurando pontos seguros de corte',
            'Generating sliced output images in memory': 'Criando páginas',
            'Saving output images to storage': 'Salvando páginas',
            'has been successfully saved': 'foi salvo',
            'Running post process on output files': 'Executando pós-processamento',
            'Working -': 'Processando -', 'Idle -': 'Parado -',
        },
        'es': {
            'Idle - Process completed in': 'Terminado en', 'seconds': 'segundos',
            'WARNING: long pages; no nearby safe cut. Review output.': 'AVISO: páginas largas; no se encontró un corte seguro cercano. Revisa el resultado.',
            'Exploring input directory for working directories': 'Buscando carpetas de imágenes',
            'Working directories were found': 'carpetas encontradas',
            'Preparing & loading images Into memory': 'Preparando y cargando imágenes',
            'Combining images into a single combined image': 'Uniendo imágenes',
            'Detecting & selecting valid slicing points': 'Buscando puntos seguros de corte',
            'Generating sliced output images in memory': 'Creando páginas',
            'Saving output images to storage': 'Guardando páginas',
            'has been successfully saved': 'se guardó',
            'Running post process on output files': 'Ejecutando posprocesamiento',
            'Working -': 'Procesando -', 'Idle -': 'Detenido -',
        },
    }
    for original, translated in parts[appearance.language].items():
        message = message.replace(original, translated)
    return message
