from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

from src.config.config import Configuration
from src.window.interface.main_settings import Ui_Dialog as MainSettingsDialog


class MainSettings(QDialog):
    def __init__(self, parent):
        super(MainSettings, self).__init__(parent=parent, flags=Qt.WindowCloseButtonHint)
        self.config = Configuration()

        self.ui = MainSettingsDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Main Settings')

        self.ui.lineEdit_input_directory.setText(self.config.config['input_directory'])
        self.ui.lineEdit_output_directory.setText(self.config.config['output_directory'])
        self.ui.pushButton_input_directory.clicked.connect(self.select_input_folder)
        self.ui.pushButton_output_directory.clicked.connect(self.select_output_folder)

        self.ui.lineEdit_input_formats.setText(' '.join(self.config.config['input_formats']))

        self.ui.spinBox_width.setValue(self.config.config['output_image_settings']['width'])
        self.ui.spinBox_height.setValue(self.config.config['output_image_settings']['height'])

        self.ui.spinBox_crop_red.setValue(self.config.config['output_image_settings']['color_limits']['red'])
        self.ui.spinBox_crop_green.setValue(self.config.config['output_image_settings']['color_limits']['green'])
        self.ui.spinBox_crop_blue.setValue(self.config.config['output_image_settings']['color_limits']['blue'])
        self.ui.spinBox_crop_alpha.setValue(self.config.config['output_image_settings']['color_limits']['alpha'])

        self.ui.spinBox_quality.setValue(self.config.config['output_image_settings']['quality'])

    # Open windows dialog for input folder
    def select_input_folder(self):
        dialog = QFileDialog()
        old_path = self.ui.lineEdit_input_directory.text()
        new_path = QFileDialog.getExistingDirectory(dialog, 'Change Input Directory', old_path,
                                                    options=QFileDialog.ShowDirsOnly)
        # Keep old path if nothing were selected
        self.ui.lineEdit_input_directory.setText(new_path if new_path != '' else old_path)

    # Open windows dialog for output folder
    def select_output_folder(self):
        dialog = QFileDialog()
        old_path = self.ui.lineEdit_output_directory.text()
        new_path = QFileDialog.getExistingDirectory(dialog, 'Change Output Directory', old_path,
                                                    options=QFileDialog.ShowDirsOnly)
        # Keep old path if nothing were selected
        self.ui.lineEdit_output_directory.setText(new_path if new_path != '' else old_path)

    # Save configuration on click 'OK' button
    def accept(self):
        self.config.config['input_directory'] = self.ui.lineEdit_input_directory.text()
        self.config.config['output_directory'] = self.ui.lineEdit_output_directory.text()
        self.config.config['input_formats'] = self.ui.lineEdit_input_formats.text().split()
        self.config.config['output_image_settings'] = {
                'width': self.ui.spinBox_width.value(),
                'height': self.ui.spinBox_height.value(),
                'quality': self.ui.spinBox_quality.value(),
                'color_limits': {
                    'red': self.ui.spinBox_crop_red.value(),
                    'green': self.ui.spinBox_crop_green.value(),
                    'blue': self.ui.spinBox_crop_blue.value(),
                    'alpha': self.ui.spinBox_crop_alpha.value()
                }
            }

        self.config.save()
        # Close the window
        self.close()
