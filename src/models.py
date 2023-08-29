import sys
import random
from dataclasses import dataclass, field

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QEvent, QObject


class TreeViewModel(QtGui.QStandardItemModel):

    def __init__(self):
        super().__init__()

        self.setHorizontalHeaderLabels([''])


    def update_item_summary_value(self, item: QtGui.QStandardItem):

        child_values = []

        for i in range(item.rowCount()):
            child_values.append(int(item.child(i).text()))

        child_summary_value = sum(map(lambda v: int(v), child_values))
        item.setText(str(child_summary_value))

        if child_summary_value >= 0:
            item.setBackground(QtGui.QColor('#9CCC65'))
        else:
            item.setBackground(QtGui.QColor('#EF5350'))

        parent = item.parent()
        if parent:
            self.update_item_summary_value(parent)


    def add_item(self, value: str, index: QtCore.QModelIndex = None):
        '''Добавить элемент в модель относительно указанного индекса'''

        # Если не указан родительский элемент (Узел), выбрать корневой элемент модели
        if index:
            parent = self.itemFromIndex(index)
        else:
            parent = self.invisibleRootItem()

        # Проверка: не является ли элемент узлом
        if index and parent.rowCount() == 0:
            # Превращение элемента в "Узел"
            parent.setEditable(False)
            # Перенос текущего значения элемента в виде "Лепестка"
            parent.appendRow(QtGui.QStandardItem(parent.text()))

        # Добавление "Лепестка"
        parent.appendRow(QtGui.QStandardItem(value))

        # Обновление суммы
        if index:
            self.update_item_summary_value(parent)


    def delete_item(self, index: QtCore.QModelIndex):
        '''Удалить элемент из модели'''

        # Удаление элемента
        self.removeRow(index.row(), index.parent())

        # Проверка остается ли родитель узлом
        parent = self.itemFromIndex(index.parent())
        if parent.rowCount() == 0:
            parent.setEditable(True)

        # Обновление значения суммы родителя
        self.update_item_summary_value(parent)
