import sqlite3
import sys
import pathlib
from jinja2 import *
from PyQt5 import QtWidgets
# from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWebEngineWidgets import QWebEngineView


def get_bases():
    main_dir = pathlib.Path("databases")
    catalog_with_bases = list()
    catalog_with_bases.append("Не выбрано")
    for name in main_dir.glob("*.db"):
        catalog_with_bases.append(name.name)
    return catalog_with_bases


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
        self.catalog_with_db.setFixedSize(300, 50)
        self.block_with_base_label.addWidget(field_base)
        self.block_with_base_label.addWidget(self.catalog_with_db)

        self.vertical_box_for_view.addLayout(self.block_with_base_label)

        category = QtWidgets.QLabel("Категория")
        self.category_catalog = QtWidgets.QComboBox()
        self.category_catalog.setFixedSize(300, 50)
        self.category_catalog.currentIndexChanged.connect(self.get_info_cur_table)

        self.block_with_category.addWidget(category)
        self.block_with_category.addWidget(self.category_catalog)

        self.bookmarks_catalog = QtWidgets.QListWidget()
        self.bookmarks_catalog.setFixedSize(500, 800)
        self.bookmarks_catalog.itemClicked.connect(self.render_main_blog)

        self.vertical_box_for_view.addLayout(self.block_with_category)
        self.vertical_box_for_view.addWidget(self.bookmarks_catalog)

        self.web_view = QWebEngineView()

        self.horizont_box = QtWidgets.QHBoxLayout()
        self.horizont_box.addLayout(self.vertical_box_for_view)

        self.horizont_box.addWidget(self.web_view)

        self.center_widget.setLayout(self.horizont_box)

    def add_to_category(self):
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
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.setFixedSize(1148, 613)
    window.show()
    sys.exit(app.exec_())
