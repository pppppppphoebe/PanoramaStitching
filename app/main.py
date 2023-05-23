from components.controller import Controller
from PyQt5 import QtWidgets
import sys

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    MainWindow = QtWidgets.QMainWindow()
    controller = Controller(MainWindow)

    MainWindow.show()
    sys.exit(app.exec_())