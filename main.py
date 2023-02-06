# import sqlite3
import pysqlite3 as sqlite3
import sys
import pathlib
from jinja2 import *
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QIcon
# from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEngineView
from flask import url_for
from PyQt5.QtCore import Qt
import psycopg2


def convert_date(values):
    day = values[2]
    month = values[1]
    year = values[0]
    return f"{day}.{month}.{year}"


def get_info_from_db_for_edit(cur_bd, table_name, record_name, index_row):
    with sqlite3.connect(cur_bd) as conn:
        cur = conn.cursor()
        res = cur.execute("""
                    SELECT * FROM `{table_name}`
                    WHERE `name` = ? and `id` = ?
                    """.format(table_name=table_name),
                          (record_name, index_row)).fetchall()
        return res


class EditRecord(QtWidgets.QWidget):
    def __init__(self, cur_bd_name, cur_category_name, bookmark_edit, function_restart_bookmarks):
        super().__init__()

        self.cur_bd_name = cur_bd_name
        self.cur_category_name = cur_category_name
        self.bookmark_for_edit = bookmark_edit
        self.restart_book = function_restart_bookmarks

        self.name_record_edit = QtWidgets.QLineEdit()
        self.name_record_edit.setPlaceholderText("Название")

        self.wb_patch_record_edit = QtWidgets.QLineEdit()
        self.wb_patch_record_edit.setPlaceholderText("Скрин-шот")
        self.wb_patch_btn = QtWidgets.QPushButton("Выбрать файл")
        self.wb_patch_btn.clicked.connect(self.select_file)

        self.date_edit = QtWidgets.QLineEdit()
        self.date_edit.setPlaceholderText("Дата")
        self.date_btn = QtWidgets.QPushButton("...")
        self.date_btn.clicked.connect(self.hide_calendar)

        self.date_widget = QtWidgets.QCalendarWidget()
        self.date_widget.hide()
        self.date_widget.selectionChanged.connect(self.add_to_date)

        self.url_edit = QtWidgets.QLineEdit()
        self.url_edit.setPlaceholderText("Ссылка")
        self.status_edit = QtWidgets.QLineEdit()
        self.status_edit.setPlaceholderText("Статус")

        self.description_edit = QtWidgets.QTextEdit()
        self.description_edit.setPlaceholderText("Описание")

        self.main_vbox = QtWidgets.QVBoxLayout()
        self.main_vbox.addWidget(self.name_record_edit)

        self.up_horizont = QtWidgets.QHBoxLayout()
        self.up_horizont.addWidget(self.wb_patch_record_edit)
        self.up_horizont.addWidget(self.wb_patch_btn)

        self.down_horizont = QtWidgets.QHBoxLayout()
        self.down_horizont.addWidget(self.date_edit)
        self.down_horizont.addWidget(self.date_btn)

        self.btn_bd_insert = QtWidgets.QPushButton("Редактировать запись")
        self.btn_bd_insert.clicked.connect(self.edit_record_in_db)

        self.main_vbox.addWidget(self.name_record_edit)
        self.main_vbox.addLayout(self.up_horizont)
        self.main_vbox.addLayout(self.down_horizont)
        self.main_vbox.addWidget(self.date_widget)
        self.main_vbox.addWidget(self.url_edit)
        self.main_vbox.addWidget(self.status_edit)
        self.main_vbox.addWidget(self.description_edit)
        self.main_vbox.addWidget(self.btn_bd_insert)
        self.setLayout(self.main_vbox)

        self.get_info_record_for_edit()

        self.show()

    def hide_calendar(self):
        if self.date_widget.isHidden():
            self.date_widget.show()
        else:
            self.date_widget.hide()

    def select_file(self):
        file = QtWidgets.QFileDialog.getOpenFileName()
        self.wb_patch_record_edit.setText(file[0])

    def add_to_date(self):
        selected_date = convert_date(self.date_widget.selectedDate().getDate())
        self.date.setText(selected_date)

    def edit_record_in_db(self):
        path = pathlib.Path('databases').joinpath(pathlib.Path(self.cur_bd_name).name).absolute()
        with sqlite3.connect(path) as conn:
            values = (
                str(self.name_record_edit.text()), str(self.wb_patch_record_edit.text()), str(self.date_edit.text()),
                str(self.url_edit.text()),
                str(self.status_edit.text()),
                str(self.description_edit.toPlainText()), self.bookmark_for_edit.currentRow() + 1)
            cur = conn.cursor()
            cur.execute("""
            UPDATE `{name}`
            SET `name` = ?,
            `screen_name` = ?,
            `date` = ?,
            `url` = ?,
            `status` = ?,
            `description` = ? 
             WHERE `id` = ?
            """.format(name=self.cur_category_name), values)
            conn.commit()
            self.restart_book()

    def get_info_record_for_edit(self):
        table_name = self.cur_category_name
        record_name = self.bookmark_for_edit.currentItem().text()
        res = get_info_from_db_for_edit(self.cur_bd_name, table_name, record_name,
                                        self.bookmark_for_edit.currentRow() + 1)
        name = res[0][1]
        path_to_screen = res[0][2]
        date_to_screen = res[0][3]
        url = res[0][4]
        status = res[0][5]
        description = res[0][6]

        self.name_record_edit.setText(name)
        self.wb_patch_record_edit.setText(path_to_screen)
        self.date_edit.setText(date_to_screen)
        self.url_edit.setText(url)
        self.status_edit.setText(status)
        self.description_edit.setText(description)


class EditorCategory(QtWidgets.QWidget):
    def __init__(self, name_cur_db, name_cur_cat, function_restart_combo):
        super().__init__()
        # self.get_name_category()
        self.name_cur_db = name_cur_db
        self.name_cur_cat = name_cur_cat
        self.restart = function_restart_combo

        self.name_category_edit = QtWidgets.QLineEdit()
        self.name_category_edit.setPlaceholderText("Название категории:")
        self.name_category_edit.setText(self.name_cur_cat)
        self.add_category_btn = QtWidgets.QPushButton("Редактировать категорию")
        self.add_category_btn.clicked.connect(self.editor_category)

        self.adder_category_vbox = QtWidgets.QVBoxLayout()
        self.adder_category_vbox.addWidget(self.name_category_edit)
        self.adder_category_vbox.addWidget(self.add_category_btn)
        self.setLayout(self.adder_category_vbox)
        self.show()

    def editor_category(self):
        with sqlite3.connect(self.name_cur_db) as conn:
            # self.text_change()
            cur = conn.cursor()
            cur.execute("""
            ALTER TABLE `{now_name_category}`
            RENAME TO `{rename_name}`;
            """.format(now_name_category=self.name_cur_cat, rename_name=self.name_category_edit.text()))
            conn.commit()
            self.restart()


class AdderRecordToBD(QtWidgets.QWidget):
    def __init__(self, cur_bd_name, cur_category_name, function_restart_bookmarks):
        super().__init__()

        self.cur_bd_name = cur_bd_name
        self.cur_category_name = cur_category_name
        self.restart_book = function_restart_bookmarks

        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText("Название")

        self.wb_patch = QtWidgets.QLineEdit()
        self.wb_patch.setPlaceholderText("Скрин-шот")
        self.wb_patch_btn = QtWidgets.QPushButton("Выбрать файл")
        self.wb_patch_btn.clicked.connect(self.select_file)

        self.date = QtWidgets.QLineEdit()
        self.date.setPlaceholderText("Дата")
        self.date_btn = QtWidgets.QPushButton("...")
        self.date_btn.clicked.connect(self.hide_calendar)

        self.date_widget = QtWidgets.QCalendarWidget()
        self.date_widget.hide()
        self.date_widget.selectionChanged.connect(self.add_to_date)

        self.url = QtWidgets.QLineEdit()
        self.url.setPlaceholderText("Ссылка")
        self.status = QtWidgets.QLineEdit()
        self.status.setPlaceholderText("Статус")

        self.description = QtWidgets.QTextEdit()
        self.description.setPlaceholderText("Описание")

        self.main_vbox = QtWidgets.QVBoxLayout()
        self.main_vbox.addWidget(self.name)

        self.up_horizont = QtWidgets.QHBoxLayout()
        self.up_horizont.addWidget(self.wb_patch)
        self.up_horizont.addWidget(self.wb_patch_btn)

        self.down_horizont = QtWidgets.QHBoxLayout()
        self.down_horizont.addWidget(self.date)
        self.down_horizont.addWidget(self.date_btn)

        self.btn_bd_insert = QtWidgets.QPushButton("Загрузить в БД")
        self.btn_bd_insert.clicked.connect(self.insert_record_in_db)

        self.main_vbox.addWidget(self.name)
        self.main_vbox.addLayout(self.up_horizont)
        self.main_vbox.addLayout(self.down_horizont)
        self.main_vbox.addWidget(self.date_widget)
        self.main_vbox.addWidget(self.url)
        self.main_vbox.addWidget(self.status)
        self.main_vbox.addWidget(self.description)
        self.main_vbox.addWidget(self.btn_bd_insert)
        self.setLayout(self.main_vbox)

        self.show()

    def select_file(self):
        file = QtWidgets.QFileDialog.getOpenFileName()
        self.wb_patch.setText(file[0])

    def add_to_date(self):
        selected_date = convert_date(self.date_widget.selectedDate().getDate())
        self.date.setText(selected_date)

    def hide_calendar(self):
        if self.date_widget.isHidden():
            self.date_widget.show()
        else:
            self.date_widget.hide()

    def edit_record_in_db(self):
        path = pathlib.Path("databases", self.cur_bd_name)
        with sqlite3.connect(path) as conn:
            values = (str(self.name.text()), str(self.wb_patch.text()), str(self.date.text()), str(self.url.text()),
                      str(self.status.text()),
                      str(self.description.toPlainText()))
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO {name}  VALUES (?,?,?,?,?,?);
            """.format(name=self.cur_category_name), values)
            conn.commit()
            self.restart_book()

    def insert_record_in_db(self):
        path = pathlib.Path("databases", self.cur_bd_name)
        with sqlite3.connect(path) as conn:
            values = (str(self.name.text()), str(self.wb_patch.text()), str(self.date.text()), str(self.url.text()),
                      str(self.status.text()),
                      str(self.description.toPlainText()))
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO {name} (`name`, `screen_name`, `date`, `url`, `status`, `description`)
            VALUES (?,?,?,?,?,?);
            """.format(name=self.cur_category_name), values)
            conn.commit()
            self.restart_book()


class AdderCategoryToBD(QtWidgets.QWidget):
    def __init__(self, name_cur_db, function_restart_combo):
        super().__init__()
        self.name_cur_db = name_cur_db
        self.restart = function_restart_combo

        self.name_category = QtWidgets.QLineEdit()
        self.name_category.setPlaceholderText("Название категории:")
        self.add_category_btn = QtWidgets.QPushButton("Добавить категорию в БД")
        self.add_category_btn.clicked.connect(self.add_category_in_db)

        self.adder_category_vbox = QtWidgets.QVBoxLayout()
        self.adder_category_vbox.addWidget(self.name_category)
        self.adder_category_vbox.addWidget(self.add_category_btn)
        self.setLayout(self.adder_category_vbox)

        self.show()

    def add_category_in_db(self):
        path = pathlib.Path("databases", self.name_cur_db)
        name_category = self.name_category.text()
        with sqlite3.connect(path) as conn:
            cur = conn.cursor()

            cur.execute("""
            CREATE TABLE `{name}` (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, screen_name text, date text, url text, status text, description text);
            """.format(name=name_category))
            conn.commit()

            self.restart()


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
        self.add_category.setIcon(QIcon("images/refresh_icon.png"))
        self.add_category.clicked.connect(self.add_category_to_bd)

        self.add_record = QtWidgets.QPushButton(parent=self)
        self.add_record.move(50, 565)
        self.add_record.setFixedSize(25, 25)
        self.add_record.setIcon(QIcon("images/refresh_icon.png"))
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

    def edit_record(self):
        self.record_editor = EditRecord(self.path_to_bd, self.name_category, self.bookmarks_catalog,
                                        self.get_info_cur_table)

    def choose_db(self):
        main = QtWidgets.QFileDialog.getOpenFileName(self, "Выберите базу данных",
                                                     filter="Databases Files (*.db)", options=QtWidgets.QFileDialog.DontUseNativeDialog)[0]
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
            # delete_selection.triggered.connect()
            if not send.itemText(self.category_catalog.currentIndex()):
                update_selection.setDisabled(True)
                delete_selection.setDisabled(True)
        if send.objectName() == "bookmarks_catalog":
            update_selection = menu.addAction("Редактиовать")
            delete_selection = menu.addAction("Удалить")
            update_selection.triggered.connect(self.edit_record)
            # delete_selection.triggered.connect()
            if not self.bookmarks_catalog.selectedItems():
                return
        action = menu.exec_(self.sender().mapToGlobal(pos))

    def add_category_to_bd(self):
        self.bd_category_win = AdderCategoryToBD(pathlib.Path(self.path_to_bd).name, self.add_to_category)

    def add_record_to_bd(self):
        self.bd_win = AdderRecordToBD(pathlib.Path(self.path_to_bd).name,
                                      self.category_catalog.itemText(self.category_catalog.currentIndex()),
                                      self.get_info_cur_table)

    def add_to_category(self):
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

    def get_info_cur_table(self):
        if not self.category_catalog.itemText(self.category_catalog.currentIndex()):
            return
        self.add_record.setEnabled(True)
        path = pathlib.Path(self.path_to_bd)
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        self.name_category = name
        if path.exists():
            with sqlite3.connect(path) as conn:
                cur = conn.cursor()
                res = cur.execute("""
                        SELECT name from `{}`
                        """.format(name)).fetchall()

                self.add_to_bookmarks(res)

    def get_data(self, name):
        path = self.path_to_bd
        category = self.category_catalog.itemText(self.category_catalog.currentIndex())

        with sqlite3.connect(path) as conn:
            cur = conn.cursor()

            res = cur.execute("""
            SELECT * from {}
            WHERE name = ?
            """.format(category), (name,)).fetchall()
            return res

    def render_main_blog(self):
        values = self.get_data(self.bookmarks_catalog.currentItem().text())
        file_loader = FileSystemLoader('')
        env = Environment(loader=file_loader)
        # env.globals.update("static")
        template = env.get_template('templates/index.html')
        path = pathlib.Path("static/style.css").absolute()
        # csslink = url_for('static/', filename='style.css')
        path = str(path)
        output = template.render(values=values, path_css=path)
        print(output)
        css = QtCore.QUrl("static/style.css")
        self.web_view.setHtml(output)
        # self.web_view.page().settings().set
        # self.web_view.settings().setUserStyleSheetUrl(QtCore.QUrl.fromLocalFile(str(path)))
        # self.web_view.load(QtCore.QUrl("static/style.css"))
        self.web_view.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(1148, 613)
    window.show()
    sys.exit(app.exec_())
