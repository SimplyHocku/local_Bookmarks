# -*- coding: utf-8 -*-
import sys
import sqlite3
from jinja2 import *
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from windows import AdderCategoryToBD, AdderRecordToBD, EditorCategory, EditRecord, WebWin
from other_functions import *
from typing import List, Dict


class MainWindow(QtWidgets.QMainWindow):
    sett = ""
    PATH_TO_DB = None

    def __init__(self):
        super().__init__()
        self.center_widget = QtWidgets.QWidget()
        self.center_widget.setStyleSheet("""
                                            background-image: url("static/work_img/main.png");
                                            """)

        self.setCentralWidget(self.center_widget)

        self.path_to_bd = None
        self.name_category = None

        self.search_book = QtWidgets.QLineEdit(parent=self)
        self.search_book.textChanged.connect(self.edit_book_cat)
        self.search_book.move(10, 50)
        self.search_book.setHidden(True)
        self.search_book.setObjectName("search_book")
        with open(Path("static/qss/search.book.qss")) as file:
            self.search_book.setStyleSheet(file.read())
        self.animation_for_search = QtCore.QPropertyAnimation(self.search_book, b"geometry")

        self.webs = list()

        self.menu = self.menuBar()

        self.menu_file_edit = self.menu.addMenu('&Файл')
        self.widget_menu = self.menu.addMenu("Виджеты")
        action_choose_db = self.menu_file_edit.addAction("Выбрать базу данных")
        self.add_category_action = self.menu_file_edit.addAction("Добавить категорию")
        self.add_record_action = self.menu_file_edit.addAction("Добавить закладку")

        action_choose_db.setShortcut("Ctrl+O")
        action_choose_db.triggered.connect(self.choose_db)

        tool_bar_anim_btn = self.widget_menu.addAction("Открыть список с закладками")
        tool_bar_anim_btn.setShortcut("Ctrl+R")
        tool_bar_anim_btn.triggered.connect(self.down_up_list)

        search_action_str = self.widget_menu.addAction("Поиск по вкладкам")
        search_action_str.setShortcut("Ctrl+F")
        search_action_str.triggered.connect(self.show_search)

        if self.path_to_bd is None:
            self.add_category_action.setDisabled(True)
        self.add_category_action.triggered.connect(self.add_category_to_bd)

        if self.path_to_bd is None:
            self.add_record_action.setDisabled(True)
        self.add_record_action.triggered.connect(self.add_record_to_bd)

        self.bookmarks_catalog = QtWidgets.QListWidget(parent=self)
        self.animation_for_book_cat = QtCore.QPropertyAnimation(self.bookmarks_catalog, b"geometry")
        self.bookmarks_catalog.setProperty("position", "up")
        self.bookmarks_catalog.setObjectName("bookmarks_catalog")
        with open(Path("static/qss/book_catalog.qss")) as file:
            self.bookmarks_catalog.setStyleSheet(file.read())
        self.bookmarks_catalog.setGeometry(QtCore.QRect(1, 5, 300, 0))
        self.bookmarks_catalog.setContextMenuPolicy(Qt.CustomContextMenu)

        self.bookmarks_catalog.customContextMenuRequested.connect(self.show_menu)
        self.bookmarks_catalog.itemDoubleClicked.connect(self.render_main_blog)

        self.category_catalog = QtWidgets.QComboBox(parent=self)
        if self.path_to_bd is None:
            self.category_catalog.setDisabled(True)

        self.category_catalog.setStatusTip("Выбрать категорию")
        self.category_catalog.setObjectName("category_catalog")
        self.category_catalog.setPlaceholderText("Категория")

        self.category_catalog.move(160, 0)
        self.category_catalog.setFixedSize(125, 20)
        self.category_catalog.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.category_catalog.currentIndexChanged.connect(self.get_info_cur_table)
        self.category_catalog.customContextMenuRequested.connect(self.show_menu)

    def gcursor(self):
        with sqlite3.connect(self.path_to_bd) as conn:
            cur = conn.cursor()
            return cur

    def show_search(self):
        if (self.path_to_bd or self.name_category) is None:
            return
        if self.bookmarks_catalog.size() == QtCore.QSize(300, 300):
            self.search_book.setHidden(False)
            self.animation_for_search.setDuration(500)
            self.animation_for_search.setStartValue(QtCore.QRect(65, 325, 280, 0))
            self.animation_for_search.setEndValue(QtCore.QRect(65, 325, 280, 40))
            self.animation_for_search.start()

    def edit_book_cat(self):
        name_searched_book = self.search_book.text()
        res = self.gcursor().execute("""
        SELECT `name`
        FROM {category_name}
        WHERE name LIKE ?;
        """.format(category_name=self.name_category), (f"{name_searched_book}%",)).fetchall()
        self.add_to_bookmarks(res)

    def down_up_list(self):
        if self.bookmarks_catalog.property("position") == "up":
            self.animation_for_book_cat.setDuration(500)
            self.animation_for_book_cat.setStartValue(QtCore.QRect(55, 10, 300, 0))
            self.animation_for_book_cat.setEndValue(QtCore.QRect(55, 20, 300, 300))
            self.animation_for_book_cat.start()
            self.bookmarks_catalog.setProperty("position", "down")
        else:
            self.animation_for_book_cat.setDuration(500)
            self.animation_for_book_cat.setStartValue(QtCore.QRect(55, 20, 300, 300))
            self.animation_for_book_cat.setEndValue(QtCore.QRect(55, 20, 300, 0))
            self.animation_for_book_cat.start()
            self.bookmarks_catalog.setProperty("position", "up")
            self.search_book.setHidden(True)

    def clear_bookmarks(self):
        self.bookmarks_catalog.clearSelection()

    def edit_name_category(self):
        self.bd_editor = EditorCategory(self.path_to_bd,
                                        self.name_category,
                                        self.add_to_category)

    def delete_cat(self):
        self.gcursor().execute("""
        DROP TABLE `{table_name}`
        """.format(table_name=self.category_catalog.itemText(self.category_catalog.currentIndex())))
        self.add_to_category()

    def edit_record(self):
        self.record_editor = EditRecord(self.path_to_bd, self.name_category, self.bookmarks_catalog,
                                        self.get_info_cur_table)

    def delete_record(self):

        category_name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        cur_record_name = self.bookmarks_catalog.currentItem().text()
        self.gcursor().execute("""
            DELETE FROM `{category_name}`
            WHERE name = '{name_record}'
            """.format(category_name=category_name, name_record=cur_record_name))
        self.bookmarks_catalog.clear()
        self.add_to_bookmarks(self.get_info_for_book())

    def choose_db(self):
        main = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите базу данных",
                                                     filter="Databases Files (*.db)",
                                                     options=QtWidgets.QFileDialog.DontUseNativeDialog)[0]
        self.path_to_bd = main
        self.PATH_TO_DB = main
        self.category_catalog.setEnabled(True)
        self.add_to_category()

    def show_menu(self, pos):
        send = self.sender()
        menu = QtWidgets.QMenu()
        if send.objectName() == "category_catalog":
            update_selection = menu.addAction("Редактиовать")
            delete_selection = menu.addAction("Удалить")
            update_selection.triggered.connect(self.edit_name_category)
            delete_selection.triggered.connect(self.delete_cat)
            if not send.itemText(self.category_catalog.currentIndex()):
                update_selection.setDisabled(True)
                delete_selection.setDisabled(True)
        if send.objectName() == "bookmarks_catalog":
            update_selection = menu.addAction("Редактиовать")
            delete_selection = menu.addAction("Удалить")
            update_selection.triggered.connect(self.edit_record)
            delete_selection.triggered.connect(self.delete_record)
            if not self.bookmarks_catalog.selectedItems():
                return
        action = menu.exec_(self.sender().mapToGlobal(pos))

    def add_category_to_bd(self):
        self.bd_category_win = AdderCategoryToBD(Path(self.path_to_bd).name, self.add_to_category)

    def add_record_to_bd(self):
        self.bd_win = AdderRecordToBD(Path(self.path_to_bd),
                                      self.category_catalog.itemText(self.category_catalog.currentIndex()),
                                      self.get_info_cur_table)

    def add_to_category(self):
        self.bookmarks_catalog.clear()
        self.category_catalog.clear()
        path = Path(self.path_to_bd)
        if path.exists():
            res = self.gcursor().execute("""
                        SELECT name FROM sqlite_schema 
                        WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                        """).fetchall()

            res = [name[0] for name in res]
            self.category_catalog.addItems(res)
            self.add_category_action.setEnabled(True)

    def add_to_bookmarks(self, values):
        self.bookmarks_catalog.clear()
        catalog_items = [QtWidgets.QListWidgetItem(item[0]) for item in values]
        for item in catalog_items:
            item.setTextAlignment(Qt.AlignCenter)
        while catalog_items:
            self.bookmarks_catalog.addItem(catalog_items.pop())

    def get_info_for_book(self) -> List:
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        path = Path(self.path_to_bd)
        if path.exists():
            res = self.gcursor().execute("""
                        SELECT name from `{}`
                        """.format(name)).fetchall()
            return res

    def get_info_cur_table(self):
        if not self.category_catalog.itemText(self.category_catalog.currentIndex()):
            return
        self.add_record_action.setEnabled(True)
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        self.name_category = name
        res = self.get_info_for_book()
        self.add_to_bookmarks(res)

    def clear_data_for_record(self, data) -> Dict:
        data_dict = dict()
        data_dict["record_name"] = data[1]
        data_dict["path_to_img_title"] = data[2]
        data_dict["date_create"] = data[3]
        data_dict["url_record"] = data[4]
        data_dict["status_record"] = data[5]
        data_dict["desc_record"] = data[6]
        data_dict["category"] = self.name_category
        data_dict["images_record"] = get_paths(data[7])

        return data_dict

    def get_data(self, name) -> Dict:
        category = self.category_catalog.itemText(self.category_catalog.currentIndex())
        res = self.gcursor().execute("""
        SELECT * from `{}`
        WHERE name = ?
        """.format(category), (name,)).fetchall()
        data = self.clear_data_for_record(res[0])

        return data

    def render_main_blog(self):
        self.webs.append(WebWin(self.path_to_bd, self.name_category, self.bookmarks_catalog))


if __name__ == "__main__":
    create_bd()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())
