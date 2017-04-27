# coding: utf-8

"""
Модуль для переключения версии PyQt.
По-умолчанию используется поселдняя 5-ая версия.
"""


PYQT_VERSION = 5


def get():
    """
    :return: возвращает текущую версию PyQt.
    """
    return PYQT_VERSION


def set(version):
    """
    :param version: версия, доступные значения 4 или 5.
    """

    global PYQT_VERSION

    if version in (4, 5):
        PYQT_VERSION = version
        print('NOW PyQt version is {}'.format(PYQT_VERSION))


def is4():
    """
    :return: возвращает True, если текущая версия 4.
    """
    return get() == 4


def is5():
    """
    :return: возвращает True, если текущая версия 5.
    """
    return get() == 5
