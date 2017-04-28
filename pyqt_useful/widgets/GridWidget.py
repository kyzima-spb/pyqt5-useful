# coding: utf-8

from pyqt_useful import PyQtVersion
# PyQtVersion.set(4)


if PyQtVersion.is5():
    from PyQt5.QtCore import Qt, pyqtSignal
    from PyQt5.QtWidgets import (
        QWidget, QTableView, QHeaderView, QToolButton, QPushButton,
        QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy,
        QAction
    )
else:
    from PyQt4.QtCore import Qt, pyqtSignal
    from PyQt4.QtGui import (
        QWidget, QTableView, QHeaderView, QToolButton, QPushButton,
        QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy,
        QAction
    )


class GridWidget(QWidget):
    onAdd = pyqtSignal(name='onAdd')
    onEdit = pyqtSignal(int, name='onEdit')
    onRemove = pyqtSignal(list, name='onRemove')
    selectionChanged = pyqtSignal(list, name='selectionChanged')

    @staticmethod
    def __disconnect(signal, slot):
        try:
            signal.disconnect(slot)
        except TypeError:
            # значит слот не был установлен ранее
            pass

    def __init__(self, *args, **kwargs):
        super(GridWidget, self).__init__(*args, **kwargs)
        self._initUi()
        self._initActions()
        self._initSygnals()
        self._initLayouts()

    def _initLayouts(self):
        self.layout = QGridLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setViewMode()

    def setViewMode(self, mode=Qt.Horizontal):
        if mode == Qt.Horizontal:
            self.layout_btn = QVBoxLayout()
            sizePolicy = (QSizePolicy.Minimum, QSizePolicy.Expanding)
            btnItemPos = (0, 1)
        else:
            self.layout_btn = QHBoxLayout()
            sizePolicy = (QSizePolicy.Expanding, QSizePolicy.Minimum)
            btnItemPos = (1, 0)

        for button in self.buttons:
            button.setSizePolicy(*sizePolicy)
            self.layout_btn.addWidget(button)

        self.layout_btn.addSpacerItem(QSpacerItem(0, 0, *sizePolicy))

        self.layout.removeWidget(self.view)
        self.layout.removeItem(self.layout.itemAtPosition(0, 1))

        self.layout.addWidget(self.view, 0, 0)
        self.layout.addLayout(self.layout_btn, *btnItemPos)

    def _initActions(self):
        self.actionAdd = QAction(u'Добавить', self)
        self.addBtn.setDefaultAction(self.actionAdd)
        self.view.addAction(self.actionAdd)

        self.actionEdit = QAction(u'Изменить', self)
        self.actionEdit.setDisabled(True)
        self.editBtn.setDefaultAction(self.actionEdit)
        self.view.addAction(self.actionEdit)

        self.actionRemove = QAction(u'Удалить', self)
        self.actionRemove.setDisabled(True)
        self.removeBtn.setDefaultAction(self.actionRemove)
        self.view.addAction(self.actionRemove)

    def _initSygnals(self):
        self.actionAdd.triggered.connect(self._onClickAddBtn)
        self.actionEdit.triggered.connect(self._onClickEditBtn)
        self.actionRemove.triggered.connect(self._onClickRemoveBtn)

    def _initUi(self):
        self.view = QTableView(parent=self)
        self.view.setContextMenuPolicy(Qt.ActionsContextMenu)

        self.view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)\
            if PyQtVersion.is5() else self.view.horizontalHeader().setResizeMode(QHeaderView.Stretch)

        self.view.setSelectionMode(self.view.ExtendedSelection)
        self.view.setSelectionBehavior(self.view.SelectRows)

        self.buttons = []

        self.addBtn = QToolButton(self)
        self.buttons.append(self.addBtn)

        self.editBtn = QToolButton(self)
        self.buttons.append(self.editBtn)

        self.removeBtn = QToolButton(self)
        self.buttons.append(self.removeBtn)

        self.setDisabled(True)

    def _onClickAddBtn(self):
        self.onAdd.emit()

    def _onClickEditBtn(self):
        selected = self.selectedRows().pop()
        self.onEdit.emit(selected)

    def _onClickRemoveBtn(self):
        self.onRemove.emit(self.selectedRows())

    def _onSelectionChanged(self):
        selected = self.selectedRows()
        self.actionEdit.setEnabled(len(selected) == 1)
        self.actionRemove.setEnabled(bool(selected))
        self.selectionChanged.emit(selected)

    def model(self):
        return self.view.model()

    def selectedRows(self):
        return self.view.selectionModel().selectedRows()

    def setModel(self, model):
        self.view.setModel(model)
        self.__disconnect(self.view.selectionModel().selectionChanged, self._onSelectionChanged)
        self.view.selectionModel().selectionChanged.connect(self._onSelectionChanged)
        self.setEnabled(True)


if __name__ == '__main__':
    if PyQtVersion.is5():
        from PyQt5.QtCore import QDateTime, QTimer
        from PyQt5.QtGui import QColor
        from PyQt5.QtWidgets import QApplication
    else:
        from PyQt4.QtCore import QDateTime, QTimer
        from PyQt4.QtGui import QApplication, QColor

    app = QApplication([])

    d = {'username': 'kyzima-spb1', 'passwprd': QDateTime.currentDateTime()}
    d2 = {'username': 'kyzima-spb2', 'passwprd': QDateTime.currentDateTime()}

    model = DictModel(['username', 'passwprd'])
    model.setHeaders([u'Пользователь', u'Пароль'])
    model.insert(model.rowCount(), d2)
    model.insert(model.rowCount(), d)
    model.insert(model.rowCount(), {'username': 'kyzima-spb3', 'passwprd': QDateTime.currentDateTime()})
    model.insert(model.rowCount(), {'username': 'kyzima-spb4', 'passwprd': QDateTime.currentDateTime()})

    grid = GridWidget()
    grid.setModel(model)
    # d1 = FormatterDelegate(u'Имя пользователя: {}')
    # grid.view.setItemDelegate(TypedDelegate())
    # grid.view.setItemDelegateForColumn(0, d1)
    # d2 = DateTimeDelegate(u'dd.MM.yyyy hh:mm')
    # grid.view.setItemDelegateForColumn(1, d2)
    grid.show()

    grid.setViewMode(Qt.Vertical)
    grid.setViewMode(Qt.Horizontal)

    QTimer.singleShot(1000, lambda : model.setData(model.index(0, 0), QColor(255, 0, 0), Qt.BackgroundRole))
    def f():
        row = model.rowCount()
        # model.insert(row, username='itmo', passwprd='789')
        model.update(row=row-1, username='itmo4', passwprd='7894')

        model.update(entity=d, username='gogo')
        model.update(entity=d2, passwprd=123)
        print(model.insert(username='newer', passwprd='kaka'))

        # d['username'] = 'gogo'
        # d2['passwprd'] = 123

        # model.refreshState(d, d2)

    QTimer.singleShot(1500, f)
    QTimer.singleShot(2000, lambda : model.removeRow(0))

    app.exec_()
