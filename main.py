import sqlite3
import sys
import pathlib
from jinja2 import *
from PyQt5 import QtWidgets
# from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWebEngineWidgets import QWebEngineView


# from PyQt5.QtCore import QDate


# def create_default_base():
#     path = pathlib.Path("databases", "default.db")
#
#     if path.exists():
#         pass
#     else:
#         with sqlite3.connect(path) as conn:
#             cur = conn.cursor()
#             cur.execute("""
#             CREATE TABLE
#             """)

def get_bases():
    main_dir = pathlib.Path("databases")
    catalog_with_bases = list()
    catalog_with_bases.append("Не выбрано")
    for name in main_dir.glob("*.db"):
        catalog_with_bases.append(name.name)
    return catalog_with_bases


def convert_date(values):
    day = values[2]
    month = values[1]
    year = values[0]
    return f"{day}.{month}.{year}"


class AdderRecordToBD(QtWidgets.QWidget):
    def __init__(self, cur_bd_name, cur_category_name):
        super().__init__()
        self.cur_bd_name = cur_bd_name
        self.cur_category_name = cur_category_name

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
        # self.date_btn.clicked.connect(self.test)

        self.url = QtWidgets.QLineEdit()
        self.url.setPlaceholderText("Ссылка")
        # self.wb_patch = QtWidgets.QFileDialog.getOpenFileName()[0]
        # self.wb_patch.currentChanged.connect(self.test)
        # self.date.clicked.connect(self.test)
        # self.date.hide()
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
        # print(self.date.selectedDate())
        if self.date_widget.isHidden():
            self.date_widget.show()
        else:
            self.date_widget.hide()

    def insert_record_in_db(self):
        # db_name = self.
        path = pathlib.Path("databases", self.cur_bd_name)
        with sqlite3.connect(path) as conn:
            values = (str(self.name.text()), str(self.wb_patch.text()), str(self.date.text()), str(self.url.text()), str(self.status.text()),
                      str(self.description.toPlainText()))
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO {name} VALUES (?,?,?,?,?,?);
            """.format(name=self.cur_category_name), values)
            conn.commit()


class AdderCategoryToBD(QtWidgets.QWidget):
    def __init__(self, name_cur_db):
        super().__init__()
        self.name_cur_db = name_cur_db

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
            CREATE TABLE `{name}` (name text, screen_name text, date text, url text, status text, description text);
            """.format(name=name_category))
            conn.commit()


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.center_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.center_widget)

        self.vertical_box_for_view = QtWidgets.QVBoxLayout()
        self.vertical_box_for_view.addStretch(10)

        self.block_with_base_label = QtWidgets.QHBoxLayout()

        self.block_with_category = QtWidgets.QHBoxLayout()

        field_base = QtWidgets.QLabel("База данных")
        self.catalog_with_db = QtWidgets.QComboBox()
        self.catalog_with_db.addItems(get_bases())
        self.catalog_with_db.currentIndexChanged.connect(self.add_to_category)
        self.catalog_with_db.setFixedSize(200, 25)
        self.block_with_base_label.addWidget(field_base)
        self.block_with_base_label.addWidget(self.catalog_with_db)

        self.vertical_box_for_view.addLayout(self.block_with_base_label)

        category = QtWidgets.QLabel("Категория")
        self.category_catalog = QtWidgets.QComboBox()
        self.category_catalog.setFixedSize(200, 25)
        self.category_catalog.currentIndexChanged.connect(self.get_info_cur_table)

        self.block_with_category.addWidget(category)
        self.block_with_category.addWidget(self.category_catalog)

        self.bookmarks_catalog = QtWidgets.QListWidget()
        self.bookmarks_catalog.setFixedSize(275, 800)
        self.bookmarks_catalog.itemClicked.connect(self.render_main_blog)

        self.add_category = QtWidgets.QPushButton("Добавить категорию")
        self.add_category.clicked.connect(self.add_category_to_bd)

        self.add_record = QtWidgets.QPushButton("Добавить запись")
        self.add_record.clicked.connect(self.add_record_to_bd)
        self.update_record = QtWidgets.QPushButton("Обновить запись")

        self.vertical_box_for_view.addLayout(self.block_with_category)

        self.vertical_box_for_view.addWidget(self.add_category)
        self.vertical_box_for_view.addWidget(self.add_record)
        self.vertical_box_for_view.addWidget(self.update_record)

        self.vertical_box_for_view.addWidget(self.bookmarks_catalog)

        self.web_view = QWebEngineView()

        self.horizont_box = QtWidgets.QHBoxLayout()
        self.horizont_box.addLayout(self.vertical_box_for_view)

        self.horizont_box.addWidget(self.web_view)

        self.center_widget.setLayout(self.horizont_box)

    def add_category_to_bd(self):
        self.bd_category_win = AdderCategoryToBD(self.catalog_with_db.itemText(self.catalog_with_db.currentIndex()))

    def add_record_to_bd(self):
        self.bd_win = AdderRecordToBD(self.catalog_with_db.itemText(self.catalog_with_db.currentIndex()),
                                      self.category_catalog.itemText(self.category_catalog.currentIndex()))

    def add_to_category(self):
        self.category_catalog.clear()
        path = pathlib.Path("databases", self.catalog_with_db.itemText(self.catalog_with_db.currentIndex()))
        if path.exists():
            with sqlite3.connect(path) as conn:
                cur = conn.cursor()
                res = cur.execute("""
                        SELECT name FROM sqlite_schema 
                        WHERE type ='table' AND name NOT LIKE 'sqlite_%';
                        """).fetchall()

                res = [name[0] for name in res]
                self.category_catalog.addItems(res)

    def add_to_bookmarks(self, values):
        self.bookmarks_catalog.clear()
        catalog_items = [item[0] for item in values]
        self.bookmarks_catalog.addItems(catalog_items)

    def get_info_cur_table(self):
        name = self.category_catalog.itemText(self.category_catalog.currentIndex())
        if not name:
            return
        base_name = self.catalog_with_db.itemText(self.catalog_with_db.currentIndex())
        path = pathlib.Path("databases", base_name)
        if path.exists():
            with sqlite3.connect(path) as conn:
                cur = conn.cursor()
                res = cur.execute("""
                        SELECT name from {}
                        """.format(name)).fetchall()

                self.add_to_bookmarks(res)

    def get_data(self, name):
        path = self.catalog_with_db.itemText(self.catalog_with_db.currentIndex())
        category = self.category_catalog.itemText(self.category_catalog.currentIndex())

        with sqlite3.connect(f"databases/{path}") as conn:
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
        template = env.get_template('templates/index.html')
        output = template.render(values=values)
        self.web_view.setHtml(output)
        self.web_view.show()


if __name__ == "__main__":
    # create_default_base()
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(1148, 613)
    window.show()
    sys.exit(app.exec_())
