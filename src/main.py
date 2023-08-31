import sys

from PyQt5 import QtWidgets

from src.models import TreeViewModel
from src.views import MainView


def main():

    app = QtWidgets.QApplication(sys.argv)

    model = TreeViewModel()

    window = MainView(model)
    window.setWindowTitle('PyQt Test App')
    window.show()

    sys.exit(app.exec())


if __name__ == '__main__':
    
    main()