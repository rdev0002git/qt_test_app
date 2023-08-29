import sys
import random
from dataclasses import dataclass, field

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QEvent, QObject

from src.models import TreeViewModel
from src.views import MainWidget


def main():

    app = QtWidgets.QApplication(sys.argv)

    model = TreeViewModel()

    window = MainWidget(model)
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    
    main()