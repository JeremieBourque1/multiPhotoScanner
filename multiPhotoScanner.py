from PySide2.QtWidgets import QApplication, QMainWindow, QLineEdit, QVBoxLayout, QMenu, QListWidgetItem,\
    QDialog, QDialogButtonBox, QLabel, QPushButton, QSlider, QListWidget, QMessageBox
from PySide2.QtUiTools import QUiLoader
from Scanner import Scanner

class MainWindow(QMainWindow):
    """
    Main window class
    """
    def __init__(self, app):
        """
        MainWindow initialization
        """
        super(MainWindow, self).__init__()
        ## app
        self.app = app
        ## ui object
        self.ui = QUiLoader().load("mainwindow.ui")
        self.ui.show()
        self.ui.setWindowTitle("multiPhotoScanner")
        self.setMinimumHeight(100)
        self.setMinimumWidth(250)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    app.exec_()
    sys.exit()

    scanner = Scanner()
    scanner.list_devices()
    scanner.list_sources()
