from send2trash import send2trash
from pathlib import Path

from PyQt5.QtCore import pyqtSlot, Qt, QThreadPool
from PyQt5.QtWidgets import QMainWindow, QStyle

from src.config.config import Configuration
from src.image_editor.image_editor import EditorManager
from src.window.main_settings import MainSettings
from src.window.advanced_settings import AdvancedSettings
from src.window.about import About
from src.window.interface.main import Ui_MainWindow as MainWindowDialog
from src.worker.worker import Worker


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__(
            parent=None,
            flags=Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui = MainWindowDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Content Image Editor')
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_TitleBarMenuButton))

        self.ui.action_main_preferenses.triggered.connect(self.show_main_settings)
        self.ui.action_main_preferenses.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        self.ui.action_advanced_preferenses.triggered.connect(self.show_advanced_settings)
        self.ui.action_advanced_preferenses.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        self.ui.action_about.triggered.connect(self.show_about)
        self.ui.action_about.setIcon(self.style().standardIcon(QStyle.SP_MessageBoxInformation))

        self.ui.pushButton_start.clicked.connect(self.start_reformat_all)
        self.ui.pushButton_start.setIcon(self.style().standardIcon(QStyle.SP_ArrowUp))

        self.ui.pushButton_start_selected.clicked.connect(self.start_reformat_selected)
        self.ui.pushButton_start_selected.setIcon(self.style().standardIcon(QStyle.SP_ArrowForward))

        self.ui.pushButton_clear_output.clicked.connect(self.clear_output_directory)
        self.ui.pushButton_clear_input.clicked.connect(self.clear_input_directory)

        self.ui.pushButton_refresh_list.clicked.connect(self.refresh)
        self.ui.pushButton_refresh_list.setIcon(self.style().standardIcon(QStyle.SP_BrowserReload))

        self.ui.pushButton_clear_selection.clicked.connect(self.clear_selection)

        self.ui.progressBar.setValue(0)
        self.dialogs = list()
        self.progress_step = None
        self.progress_current = 0
        self.images_count = 0
        self.pool = QThreadPool()

    # Show Main Settings dialog
    @pyqtSlot(name='ChangeDirectory')
    def show_main_settings(self):
        dialog = MainSettings(parent=self)
        self.dialogs.append(dialog)
        dialog.show()

    # Show Advanced Settings dialog
    @pyqtSlot(name='Settings')
    def show_advanced_settings(self):
        dialog = AdvancedSettings(parent=self)
        self.dialogs.append(dialog)
        dialog.show()

    # Show About dialog
    @pyqtSlot(name='About')
    def show_about(self):
        dialog = About(parent=self)
        self.dialogs.append(dialog)
        dialog.show()

    def refresh(self):
        files = self.get_files_in_folder()
        self.refresh_list_view(files)

    def refresh_list_view(self, files: list):
        self.ui.listWidget.clear()
        self.ui.listWidget.addItems(files)

    @staticmethod
    def get_files_in_folder():
        settings = Configuration().config
        files = Path(settings['input_directory']).iterdir()
        images_in_folder = []
        for file in (list(file for file in files)):
            if file.suffix.lower() in settings['input_formats'] and file.is_file():
                images_in_folder.append(file.name)
        return images_in_folder

    def clear_selection(self):
        self.ui.listWidget.clearSelection()

    def clear_output_directory(self):
        files = Path(Configuration().config['output_directory']).iterdir()
        for file in (list(file for file in files)):
            if file.is_file():
                send2trash(str(file))
        self.ui.progressBar.setValue(100)
        self.ui.progressBar.setFormat('Output directory cleared')

    def clear_input_directory(self):
        files = Path(Configuration().config['input_directory']).iterdir()
        for file in (list(file for file in files)):
            if file.is_file():
                send2trash(str(file))
        self.ui.progressBar.setValue(100)
        self.ui.progressBar.setFormat('Input directory cleared')

    # Closing all opened widgets when main window was closed.
    def closeEvent(self, *args, **kwargs):
        for dialog in self.dialogs:
            dialog.close()

    def start_reformat(self, images_to_work, settings, config):
        # Set main window disabled until work did not end.
        self.setEnabled(False)
        self.progress_current = 0
        self.ui.progressBar.setFormat('%p%')
        self.ui.progressBar.setValue(self.progress_current)

        self.images_count = len(images_to_work)
        # Check if there is no files in directory
        if not images_to_work:
            self.setEnabled(True)
            raise Exception("No files in input!")

        # Percentage for each image
        self.progress_step = 100 / self.images_count

        # Set maximum threads in pool
        self.pool.setMaxThreadCount(settings['worker_limit'])

        # Start external thread with main work
        for image_name in images_to_work:
            # Create new worker for function
            manager = EditorManager(
                image_name,
                settings['input_directory'],
                settings['output_directory'],
                settings['output_image_settings'],
                **config)
            worker = Worker(manager)
            # Connect signal receiver with the progress bar updating method
            worker.signals.finished.connect(self._update_progress_bar)
            worker.signals.error.connect(self._error_occurred_in_worker)
            # Run worker in thread pool
            self.pool.start(worker)

    def collect_configuration(self):
        settings = Configuration().config
        config_dict = {
            'no_rewrite': self.ui.checkBox_no_rewrite.isChecked(),
            'crop': settings['advanced_settings']['crop'],
            'square': settings['advanced_settings']['square'],
            'opaque': self.ui.checkBox_opaque.isChecked(),
            'fit': settings['advanced_settings']['fit'],
            'square_fill_color': settings['advanced_settings']['square_fill_color'],
            'opaque_fill_color': settings['advanced_settings']['opaque_fill_color'],
            'ignore_image_metadata': self.ui.checkBox_ignore_image_metadata.isChecked(),
            'simple_formats': not self.ui.checkBox_preserve_formats.isChecked()
            }
        return settings, config_dict

    def start_reformat_all(self):
        settings, config = self.collect_configuration()
        files = self.get_files_in_folder()
        self.refresh_list_view(files)
        return self.start_reformat(files, settings, config)

    def start_reformat_selected(self):
        settings, config = self.collect_configuration()
        files = [item.text() for item in self.ui.listWidget.selectedItems()]
        return self.start_reformat(files, settings, config)

    def _update_progress_bar(self):
        self.images_count -= 1
        self.progress_current += self.progress_step
        self.ui.progressBar.setValue(round(self.progress_current, 1))
        # If 100% of work is done, set main window enabled again.
        if self.images_count <= 0:
            self.ui.progressBar.setValue(100)
            self.setEnabled(True)

    def _error_occurred_in_worker(self, error):
        self._update_progress_bar()
        raise error
