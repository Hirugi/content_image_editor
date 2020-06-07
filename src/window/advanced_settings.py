from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

from src.config.config import Configuration
from src.window.interface.advanced_settings import Ui_Dialog as AdvancedSettingsDialog


class AdvancedSettings(QDialog):
    def __init__(self, parent):
        super(AdvancedSettings, self).__init__(parent=parent, flags=Qt.WindowCloseButtonHint)
        self.config = Configuration()

        self.ui = AdvancedSettingsDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('Advanced Settings')

        self.ui.checkBox_crop.setChecked(self.config.config['advanced_settings']['crop'])
        self.ui.checkBox_square.setChecked(self.config.config['advanced_settings']['square'])
        self.ui.checkBox_fit.setChecked(self.config.config['advanced_settings']['fit'])

        self.ui.checkBox_verbose.setChecked(self.config.config['verbose_errors'])

        self.ui.spinBox_worker.setValue(self.config.config['worker_limit'])

        self.ui.spinBox_square_red.setValue(self.config.config['advanced_settings']['square_fill_color']['red'])
        self.ui.spinBox_square_green.setValue(self.config.config['advanced_settings']['square_fill_color']['green'])
        self.ui.spinBox_square_blue.setValue(self.config.config['advanced_settings']['square_fill_color']['blue'])

        self.ui.spinBox_opaque_red.setValue(self.config.config['advanced_settings']['opaque_fill_color']['red'])
        self.ui.spinBox_opaque_green.setValue(self.config.config['advanced_settings']['opaque_fill_color']['green'])
        self.ui.spinBox_opaque_blue.setValue(self.config.config['advanced_settings']['opaque_fill_color']['blue'])

    # Save configuration on click 'OK' button
    def accept(self):
        self.config.config['verbose_errors'] = self.ui.checkBox_verbose.isChecked()
        self.config.config['worker_limit'] = self.ui.spinBox_worker.value()
        self.config.config['advanced_settings'] = {
                'crop': self.ui.checkBox_crop.isChecked(),
                'square': self.ui.checkBox_square.isChecked(),
                'fit': self.ui.checkBox_fit.isChecked(),
                'square_fill_color': {
                    'red': self.ui.spinBox_square_red.value(),
                    'green': self.ui.spinBox_square_green.value(),
                    'blue': self.ui.spinBox_square_blue.value()
                },
                'opaque_fill_color': {
                    'red': self.ui.spinBox_opaque_red.value(),
                    'green': self.ui.spinBox_opaque_green.value(),
                    'blue': self.ui.spinBox_opaque_blue.value()
                }
            }

        self.config.save()
        # Close the window
        self.close()
