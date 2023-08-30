from PyQt5 import QtCore, QtGui, QtWidgets


class TreeViewModel(QtGui.QStandardItemModel):

    dataUpdated = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()

        # Установка заголовка
        self.setHorizontalHeaderLabels(['Дерево'])

        # Подключения к сигналам
        self.rowsInserted.connect(self.update_node_by_changed_row)
        self.rowsRemoved.connect(self.update_node_by_changed_row)
        self.dataChanged.connect(self.update_by_changed_item)


    def item_children_value_sum(self, item: QtGui.QStandardItem):
        '''Функция возвращает сумму значений потомков элемента'''
        return sum([int(item.child(i).text()) for i in range(item.rowCount())])


    def set_item_bg_color_by_value(self, item: QtGui.QStandardItem, value: int):
        '''Установить цвет для элемента в зависимости от полученного значения'''

        if value >= 0:
            # Установить зеленый цвет фона элемента
            item.setBackground(QtGui.QColor('#9CCC65'))
        else:
            # Установить красный цвет фона элемента
            item.setBackground(QtGui.QColor('#EF5350'))


    def update_node_by_changed_row(self, index: list[QtCore.QModelIndex]):
        '''Функция обновления элемента связанного с измененной строкой'''

        # Получение элемента по индексу
        item = self.itemFromIndex(index)

        # Проверка, получен ли элемент по индексу
        # На случай если был указан индекс корневого невидимого элемента
        if item:
            
            # Если у элемента есть потомки
            if item.rowCount() != 0:
                
                # Получение суммы значений потомков
                # и указание ее в качестве значений элемента
                item_sum = self.item_children_value_sum(item)
                item.setText(str(item_sum))

                # Проверка возможности редактирования в GUI значения элемента
                # и отключение ее, если эта возможность активна, так как элемент
                # с потомками считается "Узлом", и его значения вычисляется автоматически
                if item.isEditable():
                    item.setEditable(False)

                self.set_item_bg_color_by_value(item, item_sum)

            else:
                # Если у элемента нет потомков, то это означает,
                # что обращение к этой функции вызвано удалением
                # имеющихся потомков элемента, а значит элемент стал "Листом"
                item.setText(str(0))
                item.setEditable(True)
                item.setBackground(QtGui.QColor('#FFFFFFFF'))


    def update_by_changed_item(self, index: QtCore.QModelIndex):
        '''Функция обновления родителя элемента'''

        # Получение родителя элемента
        parent = self.itemFromIndex(index).parent()

        if parent:
            children_value_sum = self.item_children_value_sum(parent)
            parent.setText(str(children_value_sum))

            self.set_item_bg_color_by_value(parent, children_value_sum)
        else:
            # Если родитель элемента не получен, значит в функцию был передан индекс
            # корневого невидимого элемента.
            # Так как вызов данный функции привязан к сигналу об изменении
            # данных элемента модели, а данная функция изменяет данные родителя элемента,
            # то через сигнал об изменении вызывает сама себя уже для родителя текущего элемента.
            # Так последовательно функция идет до корневого элемента. И получение его означает, что
            # последовательное обновление данных завершено. Для чего активируется соответствующий сигнал.
            self.dataUpdated.emit()


    def add_item(self, value: str, index: QtCore.QModelIndex = None):
        '''Добавить элемент в модель относительно указанного индекса'''

        # Если не указан родительский элемент (Узел), выбрать корневой элемент модели
        if index:
            parent = self.itemFromIndex(index)
        else:
            parent = self.invisibleRootItem()

        # Проверка: не является ли элемент узлом
        if index and parent.rowCount() == 0:

            # Перенос текущего значения элемента в виде "Лепестка"
            parent.appendRow(QtGui.QStandardItem(parent.text()))

        # Добавление "Лепестка"
        parent.appendRow(QtGui.QStandardItem(value))


    def delete_item(self, index: QtCore.QModelIndex):
        '''Удалить по индексу элемент из модели'''

        # Удаление элемента
        self.removeRow(index.row(), index.parent())


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
            и устанавливает сумму значение потомков в текстовое поле элемента
            '''
            
            if isinstance(data_for_item, list):
                for item_data in data_for_item:
                    child_item = QtGui.QStandardItem('0')
                    update_item_data(child_item, item_data)
                    item.appendRow(child_item)

                child_sum = self.item_children_value_sum(item)
                item.setText(str(child_sum))
                self.set_item_bg_color_by_value(item, child_sum)
            else:
                item.setText(str(data_for_item))

        # Создание элементов первого уровня, их наполнение
        # и добавление в корневой элемент модели.
        for data_for_item in data:
            item = QtGui.QStandardItem('0')
            update_item_data(item, data_for_item)
            root_item.appendRow(item)


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

