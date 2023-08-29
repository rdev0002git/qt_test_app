import sys
import random
from dataclasses import dataclass, field

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QEvent, QObject

from src.ui.main_widget_ui import Ui_mainWidget
from src.models import TreeViewModel


class MainWidget(Ui_mainWidget, QtWidgets.QWidget):

    def __init__(self, tree_view_model: TreeViewModel):
        super().__init__()

        # Инициализация UI
        self.setupUi(self)

        self.addTreeItemEdit.setValidator(QtGui.QIntValidator())

        # Подключение модели данных к TreeView
        self.model = tree_view_model
        self.treeView.setModel(self.model)

        # Подключения к сигналам
        self.randomizeDataButton.clicked.connect(self.load_randomize_data)
        self.addTreeItemButton.clicked.connect(self.add_tree_item)
        self.deleteTreeItemButton.clicked.connect(self.delete_tree_item)

    # TREEVIEW
    def add_tree_item(self):
        '''Функция добавляющая элемент в TreeView'''

        # Получение указанного в LineEdit значения
        value = self.addTreeItemEdit.text()

        # Валидация введенного значения
        if value == '':
            QtWidgets.QToolTip.showText(self.addTreeItemEdit.mapToGlobal(self.addTreeItemEdit.rect().bottomLeft()), "Введите целое число", self.addTreeItemEdit)
            return

        # Получение выделенного элемента в TreeView
        try: element_index = self.treeView.selectedIndexes()[0]
        except: element_index = None

        self.model.add_item(value, element_index)

    def delete_tree_item(self):
        '''Функция удаляющая выделенные элементы в TreeView'''

        indexes = self.treeView.selectedIndexes()

        for index in indexes:
            self.model.delete_item(index)

    # SIDEBAR
    def load_data(self):
        '''Функция загрузки данных в модель TreeView'''
        pass

    def save_data(self):
        '''Функция сохранения данных из модели TreeView'''
        pass

    def load_randomize_data(self):
        '''Функция заполнения TreeView рандомными данными'''
        pass