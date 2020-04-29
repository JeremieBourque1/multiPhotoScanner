import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
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
        self.app = app
        self.initUi()
        self.scanner = Scanner()
        self.picture_formats_dict = {'6x4 inch': (6, 4, "inch"), "custom": (0, 0, "inch")}
        self.units = ['inch', 'cm']

        self.pictureFormatComboBox.currentTextChanged.connect(self.updateFormatProperties)
        self.startScanButton.clicked.connect(self.startScan)

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
        self.setEnabledAllGroups(False)
        self.applyOptions()
        self.scanner.scan("test4.jpg")  # TODO: make the scan run in another QThread
        self.setEnabledAllGroups(True)  # TODO: this should be connected to the signal indicating the end of the scan



def populateComboBox(comboBox, items):
    comboBox.clear()
    comboBox.addItems(items)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow(app)
    app.exec_()
    sys.exit()
