import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QThread
from PyQt5 import uic
from .Scanner import Scanner


class ScanThread(QThread):
    """
    Thread class to run the scan
    """
    def __init__(self, mainWindow):
        super(ScanThread, self).__init__()
        self.mainWindow = mainWindow

    def run(self):
        """
        run thread
        """
        self.mainWindow.setEnabledAllGroups(False)
        self.mainWindow.startScanButton.setEnabled(False)
        self.mainWindow.cancelScanButton.setEnabled(True)
        self.mainWindow.scanner.scan()
        self.mainWindow.setEnabledAllGroups(True)
        self.mainWindow.startScanButton.setEnabled(True)
        self.mainWindow.cancelScanButton.setEnabled(False)
        self.mainWindow.scanProgress.setValue(0)

    def stop(self):
        """
        Stop thread
        """
        self.mainWindow.scanner.shouldRun = False


class MainWindow(QMainWindow):
    """
    Main window class
    """
    def __init__(self, app):
        """
        MainWindow initialization
        """
        super(MainWindow, self).__init__()
        self.app = app
        self.initUi()
        self.scanner = Scanner(self)
        self.scan_thread = ScanThread(self)
        self.picture_formats_dict = {'6x4 inch': (6, 4, "inch"), "custom": (0, 0, "inch")}
        self.units = ['inch', 'cm']

        # Connect signals
        self.pictureFormatComboBox.currentTextChanged.connect(self.updateFormatProperties)
        self.startScanButton.clicked.connect(self.startScan)
        self.cancelScanButton.clicked.connect(self.cancelScan)

        populateComboBox(self.scannerComboBox, self.makeScannerList())
        populateComboBox(self.pictureFormatComboBox, list(self.picture_formats_dict.keys()))

    def initUi(self):
        uic.loadUi('mainwindow.ui', self)
        self.show()
        self.setWindowTitle("multiPhotoScanner")

    def makeScannerList(self):
        items = []
        self.scanner.list_all_scanners(auto_set=False)
        for source in self.scanner.source_list:
            items.append(source.get_source_name())
        return items

    def updateFormatProperties(self, currentText):
        print("updating format properties to %s" % currentText)
        properties = self.picture_formats_dict[currentText]
        width = properties[0]
        height = properties[1]
        unit = properties[2]
        populateComboBox(self.unitsComboBox, [unit])
        self.heightSpinBox.setValue(height)
        self.widthSpinBox.setValue(width)
        if currentText == "custom":
            populateComboBox(self.unitsComboBox, self.units)
            self.setEnablePictureProperties(True)
        else:
            self.setEnablePictureProperties(False)

    def setEnablePictureProperties(self, state):
        self.unitsComboBox.setEnabled(state)
        self.widthSpinBox.setEnabled(state)
        self.heightSpinBox.setEnabled(state)

    def setEnabledAllGroups(self, state):
        self.picturePropertiesGroup.setEnabled(state)
        self.albumPropertiesGroup.setEnabled(state)
        self.scannerPropertiesGroup.setEnabled(state)

    def applyOptions(self):
        self.scanner.set_resolution(self.dpiSpinBox.value())
        self.scanner.set_picture_format(self.widthSpinBox.value(), self.heightSpinBox.value(),
                                        str(self.unitsComboBox.currentText()))
        self.scanner.set_active_source(self.scanner.source_dict[str(self.scannerComboBox.currentText())])
        self.scanner.set_album_directory("test_album") # TODO: apply album option
        self.scanner.set_number_of_pictures(self.nbOfPicturesSpinBox.value())
        if self.landscapeRadioButton.isChecked():
            self.scanner.set_orientation("landscape")
        else:
            self.scanner.set_orientation("portrait")

    def startScan(self):
        self.applyOptions()
        self.scan_thread.start()

    def cancelScan(self):
        print("Cancelling scan")
        self.scan_thread.stop()


def populateComboBox(comboBox, items):
    comboBox.clear()
    comboBox.addItems(items)


def main():
    # Change working directory to this script's directory to easily access mainwindow.ui
    print("Path before change: %s" % os.getcwd())
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    print("Path after change: %s" % os.getcwd())
    app = QApplication(sys.argv)
    window = MainWindow(app)
    app.exec_()
    sys.exit()
