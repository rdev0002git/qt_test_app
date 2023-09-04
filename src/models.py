from PyQt5 import QtCore, QtGui, QtWidgets


class TreeViewModel(QtGui.QStandardItemModel):

    dataUpdated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Установка заголовка
        self.setHorizontalHeaderLabels(['Дерево'])


    def update_item_parents_data(self, item: QtGui.QStandardItem):
        '''Обновить, рекурсивно, значения родителей элемента'''

        parent = item.parent()

        if parent:

            # Обновление значения родителя
            self.update_node_data(parent)
            self.update_item_parents_data(parent)


    def update_node_data(self, item: QtGui.QStandardItem):
        '''Обновить данные элемента и его потомков'''

        # Обновляем значение элемента
        children_sum = sum([int(item.child(i).text()) for i in range(item.rowCount())])
        item.setText(str(children_sum))


    def add_item(self, value: str, index: QtCore.QModelIndex = None):
        '''Добавить элемент в модель относительно указанного индекса'''

        # Если не указан индекс родительского элемента, выбрать корневой элемент модели
        if index:
            parent = self.itemFromIndex(index)
        else:
            parent = self.invisibleRootItem()

        # Если элемент не является "Узлом", превращаем в "Узел" и переносим в него имеющееся значение
        if index and parent.rowCount() == 0:

            # Перенос текущего значения элемента в виде "Лепестка"
            parent.appendRow(QtGui.QStandardItem(parent.text()))

        # Добавление нового "Лепестка"
        new_item = QtGui.QStandardItem(value)
        parent.appendRow(new_item)

        # Обновление данных родителя
        self.update_item_parents_data(new_item)

        # Сигнал об обновлении данных модели
        self.dataUpdated.emit()


    def delete_item(self, index: QtCore.QModelIndex):
        '''Удалить по индексу элемент из модели'''

        # Получение элемента родителя
        parent = self.itemFromIndex(index.parent())

        # Удаление элемента
        self.removeRow(index.row(), index.parent())

        # Обновление значения родителя
        if parent:
            self.update_node_data(parent)

            # Обновление родителей родителя
            self.update_item_parents_data(parent)

        # Сигнал о изменении данных модели
        self.dataUpdated.emit()


    def load_data(self, data: list):

        # Очистка текущих данных Модели
        self.clear()
        self.setHorizontalHeaderLabels(['Дерево'])

        # Получение корневого элемента модели
        root_item = self.invisibleRootItem()

        def update_item_data(item: QtGui.QStandardItem, data_for_item: int | list):
            '''
            Функция заполняет данными и преобразует полученный элемент в соответствии с типом данных.
            Если int - то устанавливает это значение в текстовое поле элемента.
            Если list - проходит по списку, создавая потомков элемента, добавляет в них данные
            '''

            if isinstance(data_for_item, list):
                for item_data in data_for_item:
                    child_item = QtGui.QStandardItem('0')
                    update_item_data(child_item, item_data)
                    self.update_node_data(item)
                    item.appendRow(child_item)
            else:
                item.setText(str(data_for_item))

        # Создание элементов первого уровня, их наполнение
        # и добавление в корневой элемент модели.
        for data_for_item in data:
            item = QtGui.QStandardItem('0')
            update_item_data(item, data_for_item)
            root_item.appendRow(item)

        self.dataUpdated.emit()


    def get_data(self):
        '''Получить данные содержащиеся в модели'''

        def get_item_data(item: QtGui.QStandardItem):
            '''Получить значения элемента и его потомков'''

            item_data = []

            for i in range(item.rowCount()):
                child_item = item.child(i)

                if child_item.rowCount() != 0:
                    item_data.append(get_item_data(child_item))
                else:
                    item_data.append(int(child_item.text()))

            return item_data

        return get_item_data(self.invisibleRootItem())

