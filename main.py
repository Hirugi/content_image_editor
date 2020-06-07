import sys
import traceback

from PyQt5.QtWidgets import QApplication, QMessageBox

from src.window.main import MainWindow
from src.config.config import Configuration


def start():
    """
    Creating application and show the main GUI window.
    """
    widget = MainWindow()
    widget.show()
    return widget


def excepthook(exc_type, exc_value, exc_tb):
    """
    Except hook to rewrite standard excepthook.
    Shows exceptions as QMessageBox
    """
    error = QMessageBox()
    error.setIcon(QMessageBox.Critical)
    error.setText(f'{exc_value}')
    try:
        verbose = Configuration().config['verbose_errors']
    except KeyError:
        verbose = True

    if verbose:
        except_type = exc_type.__name__
        except_trace = '\n'.join(traceback.format_tb(exc_tb))
        error.setInformativeText(f'{except_type}: \n\n{except_trace}')
    error.setWindowTitle("Error")
    return error.exec_()


if __name__ == '__main__':
    sys._excepthook = sys.excepthook
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    w = start()
    sys.exit(app.exec_())
