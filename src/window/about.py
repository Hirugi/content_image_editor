from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QFileDialog

from src.window.interface.about import Ui_Dialog as AboutDialog


class About(QDialog):
    def __init__(self, parent):
        super(About, self).__init__(parent=parent, flags=Qt.WindowCloseButtonHint)

        self.ui = AboutDialog()
        self.ui.setupUi(self)
        self.setWindowTitle('About')
