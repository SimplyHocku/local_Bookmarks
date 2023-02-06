#-*- coding: utf-8 -*-
import sys
import pathlib
import sqlite3
from jinja2 import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt
from windows import AdderCategoryToBD, AdderRecordToBD, EditorCategory, EditRecord
from other_functions import *


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.center_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.center_widget)

        self.path_to_bd = None
        self.name_category = None

        self.menu = self.menuBar()
        self.menu_file_edit = self.menu.addMenu('&Файл')
        action_choose_db = self.menu_file_edit.addAction("Выбрать базу данных")
        action_choose_db.triggered.connect(self.choose_db)

        self.bookmarks_catalog = QtWidgets.QListWidget(parent=self)
        self.bookmarks_catalog.setObjectName("bookmarks_catalog")
        self.bookmarks_catalog.move(10, 30)
        self.bookmarks_catalog.setFixedSize(276, 530)
        self.bookmarks_catalog.setContextMenuPolicy(Qt.CustomContextMenu)

        self.bookmarks_catalog.customContextMenuRequested.connect(self.show_menu)
        self.bookmarks_catalog.itemDoubleClicked.connect(self.render_main_blog)

        self.web_view = QWebEngineView(parent=self)
        self.web_view.settings()
        self.web_view.setStyleSheet("databases")
        self.web_view.setFixedSize(840, 530)
        self.web_view.move(300, 30)

        self.add_category = QtWidgets.QPushButton(parent=self)
        if self.path_to_bd is None:
            self.add_category.setDisabled(True)
        self.add_category.move(10, 565)
        self.add_category.setFixedSize(25, 25)
        self.add_category.setIcon(QIcon("images/add_record.png"))
        self.add_category.clicked.connect(self.add_category_to_bd)

        self.add_record = QtWidgets.QPushButton(parent=self)
        self.add_record.move(50, 565)
        self.add_record.setFixedSize(25, 25)
        self.add_record.setIcon(QIcon("images/add_category.png"))

        self.add_record.clicked.connect(self.add_record_to_bd)

        self.category_catalog = QtWidgets.QComboBox(parent=self)
        if self.path_to_bd is None:
            self.category_catalog.setDisabled(True)
        if not self.category_catalog.isEnabled():
            self.add_record.setDisabled(True)
        self.category_catalog.setStatusTip("Выбрать категорию")
        self.category_catalog.setObjectName("category_catalog")
        self.category_catalog.setPlaceholderText("Категория")

        self.category_catalog.move(160, 565)
        self.category_catalog.setFixedSize(125, 25)
        self.category_catalog.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)

        self.category_catalog.currentIndexChanged.connect(self.get_info_cur_table)
        self.category_catalog.customContextMenuRequested.connect(self.show_menu)

    def clear_bookmarks(self):
        self.bookmarks_catalog.clearSelection()

    def edit_name_category(self):
        self.bd_editor = EditorCategory(self.path_to_bd,
                                        self.name_category,
                                        self.add_to_category)

    def delete_cat(self):
        with sqlite3.connect(self.path_to_bd) as conn:
            cur = conn.cursor()
            cur.execute("""
            DROP TABLE `{table_name}`
            """.format(table_name=self.category_catalog.itemText(self.category_catalog.currentIndex())))
            conn.commit()
            self.add_to_category()

    def edit_record(self):
        self.record_editor = EditRecord(self.path_to_bd, self.name_category, self.bookmarks_catalog,
                                        self.get_info_cur_table)

    def delete_record(self):
        with sqlite3.connect(self.path_to_bd) as conn:
            cur = conn.cursor()
            category_name = self.category_catalog.itemText(self.category_catalog.currentIndex())
            cur_record_name = self.bookmarks_catalog.currentItem().text()
            cur.execute("""
            DELETE FROM `{category_name}`
            WHERE name = '{name_record}'
            """.format(category_name=category_name, name_record=cur_record_name))
            conn.commit()
            self.bookmarks_catalog.clear()
            self.add_to_bookmarks(self.get_info_for_book())

    def choose_db(self):
        main = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите базу данных",
                                                     filter="Databases Files (*.db)",
                                                     options=QtWidgets.QFileDialog.DontUseNativeDialog)[0]
        self.path_to_bd = main
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
        self.bd_category_win = AdderCategoryToBD(pathlib.Path(self.path_to_bd).name, self.add_to_category)

    def add_record_to_bd(self):
        self.bd_win = AdderRecordToBD(pathlib.Path(self.path_to_bd),
                                      self.category_catalog.itemText(self.category_catalog.currentIndex()),
                                      self.get_info_cur_table)

    def add_to_category(self):
        self.bookmarks_catalog.clear()
        self.category_catalog.clear()
        path = pathlib.Path(self.path_to_bd)
        if path.exists():
            with sqlite3.connect(path) as conn:
                cur = conn.cursor()
                res = cur.execute("""
                        SELECT name FROM sqlite_schema 
                        WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                        """).fetchall()

                res = [name[0] for name in res]
                self.category_catalog.addItems(res)
                self.add_category.setEnabled(True)

    def add_to_bookmarks(self, values):
        self.bookmarks_catalog.clear()
        catalog_items = [item[0] for item in values]
        self.bookmarks_catalog.addItems(catalog_items)

    def get_info_for_book(self):
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        path = pathlib.Path(self.path_to_bd)
        if path.exists():
            with sqlite3.connect(path) as conn:
                cur = conn.cursor()
                res = cur.execute("""
                        SELECT name from `{}`
                        """.format(name)).fetchall()
                return res

    def get_info_cur_table(self):
        if not self.category_catalog.itemText(self.category_catalog.currentIndex()):
            return
        self.add_record.setEnabled(True)
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        self.name_category = name
        res = self.get_info_for_book()

        self.add_to_bookmarks(res)

    def get_data(self, name):
        path = self.path_to_bd
        category = self.category_catalog.itemText(self.category_catalog.currentIndex())

        with sqlite3.connect(path) as conn:
            cur = conn.cursor()

            res = cur.execute("""
            SELECT * from `{}`
            WHERE name = ?
            """.format(category), (name,)).fetchall()
            return res

    def render_main_blog(self):
        values = self.get_data(self.bookmarks_catalog.currentItem().text())
        file_loader = FileSystemLoader('')
        env = Environment(loader=file_loader)
        template = env.get_template('templates/index.html')
        path = pathlib.Path("static/style.css").absolute()
        output = template.render(values=values, path_css=path)
        self.web_view.setHtml(output)
        self.web_view.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(1148, 613)
    # window
    window.show()
    sys.exit(app.exec_())
