import sqlite3
import pathlib
from PyQt5 import QtWidgets, QtCore, QtWebEngineWidgets
from jinja2 import *
from other_functions import *


class WebWin(QtWebEngineWidgets.QWebEngineView):
    def __init__(self, path, category, book):
        super().__init__()

        self.path_to_db = path
        self.category = category
        self.book_catalog = book
        self.cur_render()

        self.showMaximized()

    def clear_data_for_record(self, data):
        data_dict = dict()
        data_dict["record_name"] = data[1]
        data_dict["path_to_img_title"] = data[2]
        data_dict["date_create"] = data[3]
        data_dict["url_record"] = data[4]
        data_dict["status_record"] = data[5]
        data_dict["desc_record"] = data[6]
        data_dict["category"] = self.category
        data_dict["images_record"] = get_paths(data[7])

        return data_dict

    def get_dataa(self, name):

        path = self.path_to_db
        category = self.category

        with sqlite3.connect(path) as conn:
            cur = conn.cursor()

            res = cur.execute("""
                    SELECT * from `{}`
                    WHERE name = ?
                    """.format(category), (name,)).fetchall()
            data = self.clear_data_for_record(res[0])

            return data

    def cur_render(self):
        self.load((QtCore.QUrl("about:blank")))

        values = self.get_dataa(self.book_catalog.currentItem().text())
        if not values["images_record"][0]:
            values["images_record"] = [pathlib.Path("static/work_img/g.png").absolute() for _ in range(3)]
        if not values["path_to_img_title"]:
            values["path_to_img_title"] = pathlib.Path("static/work_img/page_not.png").absolute()
        file_loader = FileSystemLoader('')
        env = Environment(loader=file_loader)
        template = env.get_template('templates/index.html')
        output = template.render(values=values)

        with open("templates/output.html", "wb") as file:
            file.write(output.encode("utf-8"))

        path = pathlib.Path("templates/output.html").absolute()
        self.setUrl(QtCore.QUrl().fromLocalFile(str(path)))


class EditRecord(QtWidgets.QWidget):
    def __init__(self, cur_bd_name, cur_category_name, bookmark_edit, function_restart_bookmarks):
        super().__init__()

        self.cur_bd_name = cur_bd_name
        self.cur_category_name = cur_category_name
        self.bookmark_for_edit = bookmark_edit
        self.restart_book = function_restart_bookmarks

        self.name_record_edit = QtWidgets.QLineEdit()
        self.name_record_edit.setPlaceholderText("Название")

        self.name_record_edit.textChanged.connect(self.check_name_record)

        self.label_msg = QtWidgets.QLabel("Указанное имя уже существует", parent=self)
        self.label_msg.setStyleSheet("color: red")
        self.label_msg.setGeometry(QtCore.QRect(70, 70, 200, 50))
        self.label_msg.move(60, 20)
        self.label_msg.hide()

        effect = QtWidgets.QGraphicsOpacityEffect(self.label_msg)
        self.label_msg.setGraphicsEffect(effect)

        self.animation_for_msg_label = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation_for_msg_label.setDuration(5000)
        self.animation_for_msg_label.setStartValue(1)
        self.animation_for_msg_label.setEndValue(0)

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

        self.images_for_record_edit = QtWidgets.QTextEdit()
        self.btn_select_images_edit = QtWidgets.QPushButton("Выбрать картинки")
        self.btn_select_images_edit.clicked.connect(self.select_images)

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
        self.main_vbox.addWidget(self.images_for_record_edit)
        self.main_vbox.addWidget(self.btn_select_images_edit)
        self.main_vbox.addWidget(self.btn_bd_insert)
        self.setLayout(self.main_vbox)

        self.get_info_record_for_edit()

        self.show()

    def select_images(self):
        main = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите базу данных",
                                                      # filter="Databases Files (*.jpeg), test (*.png)" "All (*.)",
                                                      options=QtWidgets.QFileDialog.DontUseNativeDialog)

        self.images_for_record_edit.setText(",".join(main[0]))

    def check_name_record(self):
        with sqlite3.connect(self.cur_bd_name) as conn:
            cur = conn.cursor()
            category = self.cur_category_name
            res = cur.execute("""
            SELECT name from '{category}';
            """.format(category=category)).fetchall()
            res = [name[0] for name in res]
            if res.count(self.name_record_edit.text()) <= 1:
                self.btn_bd_insert.setDisabled(False)
            else:
                self.label_msg.show()
                self.animation_for_msg_label.start()
                self.btn_bd_insert.setDisabled(True)

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
        self.date_edit.setText(selected_date)

    def edit_record_in_db(self):
        with sqlite3.connect(self.cur_bd_name) as conn:
            values = (
                str(self.name_record_edit.text()), str(self.wb_patch_record_edit.text()), str(self.date_edit.text()),
                str(self.url_edit.text()),
                str(self.status_edit.text()),
                str(self.description_edit.toPlainText()), str(self.images_for_record_edit.toPlainText()),
                str(self.bookmark_for_edit.currentItem().text()))
            cur = conn.cursor()
            cur.execute("""
            UPDATE `{name}`
            SET `name` = ?,
            `screen_name` = ?,
            `date` = ?,
            `url` = ?,
            `status` = ?,
            `description` = ?,
            `images` = ?
            WHERE name = ?
            """.format(name=self.cur_category_name), values)
            conn.commit()
            self.restart_book()
            self.close()

    def get_info_record_for_edit(self):
        table_name = self.cur_category_name
        record_name = self.bookmark_for_edit.currentItem().text()
        res = get_info_from_db_for_edit(self.cur_bd_name, table_name, record_name)
        name = res[0][1]
        path_to_screen = res[0][2]
        date_to_screen = res[0][3]
        url = res[0][4]
        status = res[0][5]
        description = res[0][6]
        images = res[0][7]

        self.name_record_edit.setText(name)
        self.wb_patch_record_edit.setText(path_to_screen)
        self.date_edit.setText(date_to_screen)
        self.url_edit.setText(url)
        self.status_edit.setText(status)
        self.description_edit.setText(description)
        self.images_for_record_edit.setText(images)


class EditorCategory(QtWidgets.QWidget):
    def __init__(self, name_cur_db, name_cur_cat, function_restart_combo):
        super().__init__()
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
        self.name.textChanged.connect(self.check_name_record)

        self.label_msg = QtWidgets.QLabel("Указанное имя уже существует", parent=self)
        self.label_msg.setStyleSheet("color: red")
        self.label_msg.setGeometry(QtCore.QRect(70, 70, 200, 50))
        self.label_msg.move(60, 20)
        self.label_msg.hide()

        effect = QtWidgets.QGraphicsOpacityEffect(self.label_msg)
        self.label_msg.setGraphicsEffect(effect)

        self.animation_for_msg_label = QtCore.QPropertyAnimation(effect, b"opacity")
        self.animation_for_msg_label.setDuration(5000)
        self.animation_for_msg_label.setStartValue(1)
        self.animation_for_msg_label.setEndValue(0)

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

        self.images_for_record = QtWidgets.QTextEdit()
        self.btn_select_images = QtWidgets.QPushButton("Выбрать картинки")
        self.btn_select_images.clicked.connect(self.select_images)

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
        self.main_vbox.addWidget(self.images_for_record)
        self.main_vbox.addWidget(self.btn_select_images)
        self.main_vbox.addWidget(self.btn_bd_insert)
        self.setLayout(self.main_vbox)

        self.show()

    def select_images(self):
        main = QtWidgets.QFileDialog.getOpenFileNames(self, "Выберите базу данных",
                                                      filter="Databases Files (*.jpeg), test (*.png)",
                                                      options=QtWidgets.QFileDialog.DontUseNativeDialog)

        self.images_for_record.setText(",".join(main[0]))

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

    def check_name_record(self):
        with sqlite3.connect(self.cur_bd_name) as conn:
            cur = conn.cursor()
            category = self.cur_category_name
            res = cur.execute("""
            SELECT name from '{category}';
            """.format(category=category)).fetchall()
            res = [name[0] for name in res]
            if self.name.text() in res:
                self.label_msg.show()
                self.animation_for_msg_label.start()
                self.btn_bd_insert.setDisabled(True)
            else:
                self.btn_bd_insert.setDisabled(False)

    def insert_record_in_db(self):
        path = pathlib.Path("databases", self.cur_bd_name)
        with sqlite3.connect(path) as conn:
            values = (str(self.name.text()), str(self.wb_patch.text()), str(self.date.text()), str(self.url.text()),
                      str(self.status.text()),
                      str(self.description.toPlainText()), str(self.images_for_record.toPlainText()))
            cur = conn.cursor()
            cur.execute("""
            INSERT INTO `{name}` (`name`, `screen_name`, `date`, `url`, `status`, `description`, `images`)
            VALUES (?,?,?,?,?,?,?);
            """.format(name=self.cur_category_name), values)
            conn.commit()
            self.restart_book()
            self.close()


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
            CREATE TABLE `{name}` 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, name text, screen_name text,
            date text, url text, status text, description text, images text);
            """.format(name=name_category))
            conn.commit()

            self.restart()
