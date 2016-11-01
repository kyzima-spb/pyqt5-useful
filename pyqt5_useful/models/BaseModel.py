# -*- coding: utf-8 -*-

from PyQt5.QtCore import (
    Qt, QObject, QVariant,
    QAbstractListModel, QAbstractTableModel, QModelIndex
)


class MetaData(QObject):
    @staticmethod
    def __index2str(index):
        return '{}x{}'.format(index.row(), index.column())

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__data = {}

    def get(self, key, role=Qt.DisplayRole):
        if isinstance(key, QModelIndex):
            if not key.isValid():
                return QVariant()
            key = self.__index2str(key)

        if role in self.__data:
            if key in self.__data[role]:
                return self.__data[role][key]

        return QVariant()

    def set(self, key, value, role=Qt.EditRole):
        if isinstance(key, QModelIndex):
            if not key.isValid():
                return False
            key = self.__index2str(key)

        if role not in self.__data:
            self.__data[role] = {}

        self.__data[role][key] = value

        return True


class AbstractListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__columns_data = MetaData(self)

    def data(self, index, role=Qt.DisplayRole):
        return self.__columns_data.get(index, role)

    def setData(self, index, value, role=Qt.EditRole):
        return self.__columns_data.set(index, value, role)


class AbstractTableModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.__columns_data = MetaData(self)
        self.__h_headers_data = MetaData(self)

    def data(self, index, role=Qt.DisplayRole):
        return self.__columns_data.get(index, role)

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if section < self.columnCount():
                return self.__h_headers_data.get(section, role) # @fixme: empty, call parent
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def headers(self, orientation=Qt.Horizontal):
        for section in range(self.columnCount()):
            yield self.headerData(section, orientation, Qt.DisplayRole)

    def setData(self, index, value, role=Qt.EditRole):
        return self.__columns_data.set(index, value, role)

    def setHeaderData(self, section, orientation, value, role=Qt.EditRole):
        if orientation == Qt.Horizontal and section < self.columnCount():
            ok = self.__h_headers_data.set(section, value, role)

            if ok:
                self.headerDataChanged.emit(orientation, section, section)

            return ok

        return False

    def setHeaders(self, headers, orientation=Qt.Horizontal):
        for section, value in enumerate(headers):
            self.setHeaderData(section, orientation, value, Qt.DisplayRole)


class AbstractObjectModel(AbstractTableModel):
    def __init__(self, mapping, parent=None):
        super().__init__(parent)
        self.__mapping = mapping
        self.__data = []

    def columnCount(self, pindex=None):
        return 0 if pindex and pindex.isValid() else len(self.mapping())

    def _getattr(self, entity, prop):
        raise NotImplementedError('AbstractObjectModel._getattr() is abstract and must be overridden')

    def _setattr(self, entity, prop, value):
        raise NotImplementedError('AbstractObjectModel._setattr() is abstract and must be overridden')

    def getPrototype(self):
        raise NotImplementedError('AbstractObjectModel.getPrototype() is abstract and must be overridden')

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return QVariant()

        if role in (Qt.DisplayRole, Qt.EditRole):
            obj = self.datalist()[index.row()]
            prop = self.mapping()[index.column()]
            return QVariant(self._getattr(obj, prop))

        return super().data(index, role)

    def datalist(self):
        return self.__data

    def insert(self, row, entity):
        if self.validate(entity):
            self.beginInsertRows(QModelIndex(), row, 1)
            self.datalist().insert(row, entity)
            self.endInsertRows()
            return True
        return False

    def insertRows(self, row, count, pindex=None):
        self.beginInsertRows(pindex, row, row + count - 1)
        for i in range(count):
            self.datalist().insert(row, self.getPrototype())
        self.endInsertRows()
        return True

    def mapping(self):
        if self.__mapping:
            return self.__mapping

        raise RuntimeError('Mapping not exists')

    def rowCount(self, pindex=None):
        return 0 if pindex and pindex.isValid() else len(self.datalist())

    def setData(self, index, value, role=Qt.EditRole):
        if not index.isValid():
            return False

        if role == Qt.EditRole:
            obj = self.datalist()[index.row()]
            prop = self.mapping()[index.column()]
            ret = self._setattr(obj, prop, value)

            if ret:
                self.dataChanged.emit(index, index)

            return ret

        return super().setData(index, value, role)

    def setMapping(self, mapping):
        if not isinstance(mapping, (list, tuple)):
            raise TypeError('Not list or tuple')

        if self.__mapping:
            raise RuntimeError('Mapping already set')

        self.__mapping = mapping

    def removeRows(self, row, count, pindex=None):
        self.beginRemoveRows(pindex, row, row + count - 1)
        for i in range(count):
            self.datalist().pop(row)
        self.endRemoveRows()
        return True

    def validate(self, entity):
        raise NotImplementedError('AbstractObjectModel.getPrototype() is abstract and must be overridden')


class ObjectModel(AbstractObjectModel):
    def _getattr(self, entity, prop):
        return getattr(entity, prop) if hasattr(entity, prop) else None

    def _setattr(self, entity, prop, value):
        if hasattr(entity, prop):
            setattr(entity, prop, value)
            return True
        return False

    def validate(self, entity):
        return isinstance(entity, self.getPrototype().__class__)


class DictModel(ObjectModel):
    def _getattr(self, entity, prop):
        return entity.get(prop)

    def _setattr(self, entity, prop, value):
        entity[prop] = value
        return True

    def getPrototype(self):
        proto = {}
        mapping = self.mapping()
        for key in mapping:
            proto[key] = None
        return proto

    def validate(self, entity):
        if not isinstance(entity, dict):
            return False

        mapping = self.mapping()

        for key in entity.keys():
            if key not in mapping:
                return False

        return True
