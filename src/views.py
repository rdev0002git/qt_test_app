import json

from PyQt5 import QtCore, QtGui, QtWidgets
import h5py
import numpy
import pyqtgraph

from src.ui.main_widget_ui import Ui_mainWidget
from src.models import TreeViewModel
from src.tools import gen_random_tree, hdf5_read_recursive, hdf5_write_recursive


class IntDelegate(QtWidgets.QItemDelegate):
    '''Класс реализующий методы для создания, настройки и валидации редактора элемента дерева TreeView.'''

    def createEditor(self, parent: QtWidgets.QWidget, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex):
        '''
        Создает редактор QLineEdit с ограничением на ввод определенных данных,
        допускаются только int значения
        '''

        editor = QtWidgets.QLineEdit(parent)
        editor.setValidator(QtGui.QIntValidator())
        return editor


class MainView(Ui_mainWidget, QtWidgets.QWidget):

    def __init__(self, tree_view_model: TreeViewModel):
        super().__init__()

        # Построение UI элемента
        self.setupUi(self)
        self.graph_widget = pyqtgraph.PlotWidget()
        self.graph_plot = self.graph_widget.plot([], [])
        self.graphLayout.addWidget(self.graph_widget)

        # Установка делегата для элементов TreeView
        self.treeView.setItemDelegate(IntDelegate())
        self.addTreeItemEdit.setValidator(QtGui.QIntValidator())

        # Подключение модели данных к TreeView
        self.model = tree_view_model
        self.treeView.setModel(self.model)

        # Подключения методов к сигналам
        self.addTreeItemButton.clicked.connect(self.add_tree_item)
        self.deleteTreeItemButton.clicked.connect(self.delete_tree_item)
        self.loadDataButton.clicked.connect(self.load_data)
        self.saveDataButton.clicked.connect(self.save_data)
        self.randomizeDataButton.clicked.connect(self.load_randomize_data)
        self.model.dataUpdated.connect(self.update_graph)


    # TREEVIEW
    def add_tree_item(self):
        '''Добавить элемент в TreeView'''

        # Получение введенного пользователем значения из элемента GUI
        value = self.addTreeItemEdit.text()

        # Валидация введенного значения
        if value == '':
            QtWidgets.QToolTip.showText(self.addTreeItemEdit.mapToGlobal(self.addTreeItemEdit.rect().bottomLeft()), "Нельзя добавить пустое значение!", self.addTreeItemEdit)
            return

        # Получение выделенного элемента в TreeView
        try: element_index = self.treeView.selectedIndexes()[0]
        except: element_index = None

        self.model.add_item(value, element_index)

        self.update_graph()

    def delete_tree_item(self):
        '''Удалить выделенные элементы из TreeView'''

        # Получение индексов выделенных элементов
        indexes = self.treeView.selectedIndexes()

        # Сортировка индексов от большего к меньшему, чтобы избежать проблемы смещения индексов при удалении
        indexes = sorted(indexes, key=lambda i: i.row(), reverse=True)

        def get_index_level(index: QtCore.QModelIndex):
            '''Получения числа основанного на номерах строк индексов родителей'''

            levels = []

            parent = index.parent()
            
            if parent.row() != -1:
                levels += get_index_level(parent)
                levels.append(str(index.row()))

            if len(levels) != 0: return levels
            else: return [str(index.row())]

        indexes_with_level = [(index, int(''.join(get_index_level(index)))) for index in indexes]
        indexes = [el[0] for el in sorted(indexes_with_level, key=lambda i: i[1], reverse=True)]

        # Последовательное удаление элементов
        for index in indexes:
            self.model.delete_item(index)

        self.update_graph()

    # SIDEBAR
    def load_data(self):
        '''Загрузить данные в TreeView'''
        
        # Вызов диалогового окна для получения пути к файлу и требуемые тип файла из которого будут загружаться данные
        file_path, file_path_filters = QtWidgets.QFileDialog().getOpenFileName(self, 'Открыть файл', '.', '*.json;;*.hdf5')
        if file_path == '': return

        if file_path_filters == '*.json':
            file_data = json.load(open(file_path, encoding='utf-8'))
        else:
            with h5py.File(file_path) as file:
                file_data = hdf5_read_recursive(file)

        self.model.load_data(file_data)

        self.update_graph()

    def save_data(self):
        '''Сохранить данные из TreeView'''

        # Вызов диалогового окна для получения пути к файлу и требуемые тип файла в котором нужно сохранить данные
        file_path, file_path_filters = QtWidgets.QFileDialog().getSaveFileName(self, 'Сохранить файл', '.', '*.json;;*.hdf5')
        if file_path == '': return

        data = self.model.get_data()

        if file_path_filters == '*.json':
            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, indent='    ')
        else:
            with h5py.File(file_path, 'w') as file:
                hdf5_write_recursive(file, data)

    def load_randomize_data(self):
        '''Заполнить TreeView рандомными данными'''

        data = gen_random_tree(3, 10, -33, 33, 4)
        self.model.load_data(data)

        self.update_graph()

    def update_graph(self):
        '''Обновить график'''
        
        def prepare_arr_for_graph(data: list, level: int = 0):
            '''
            Извлечь данные, из указанного иерархического списка,
            в виде массива: level - уровень вложенности в дереве, value- значение
            '''

            arr: list[tuple[int | int]] = []

            for data_item in data:

                if isinstance(data_item, list):
                    # Рекурсивное извлечение данных из "Узла"
                    values = prepare_arr_for_graph(data_item, level + 1)

                    # Добавление суммы "Узла" из полученных значений
                    arr.append((level, sum([value[1] for value in values if value[0] == level + 1])))

                    arr += values
                else:
                    arr.append((level, data_item))

            return arr

        # Получение данных из модели TreeView
        data = self.model.get_data()

        # Очистка данных графика
        self.graph_widget.plotItem.clear()

        # Если есть данные на основе которых можно построить график
        if len(data) > 0:

            # Преобразование данных в двумерный массив
            data_for_graph = prepare_arr_for_graph(data)
            print(data_for_graph)
            data_array = numpy.array(data_for_graph)

            # Извлечение уникальных уровней
            levels = numpy.unique(data_array[:, 0])

            # Вычисление сумм лепестков для каждого уровня
            level_sums = [numpy.average(data_array[data_array[:, 0] == level, 1]) for level in levels]

            # Создание нового двухмерного массива вида (level, level sum)
            result_array = numpy.column_stack((levels, level_sums))

            # Построение графика
            self.graph_widget.plot(result_array[:, 0], result_array[:, 1])