import sys
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QLabel, QWidget, QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QComboBox, QMessageBox, QToolBar
from PyQt6.QtGui import QAction, QIcon
import sqlite3
from PyQt6.QtCore import Qt, QTimer


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Student Management System')
        self.setMinimumSize(450, 600)

        file_menu_item = self.menuBar().addMenu('&File')
        help_menu_item = self.menuBar().addMenu('&Help')
        edit_menu_item = self.menuBar().addMenu('&Edit')

        add_student_action = QAction(QIcon('icons/add.png'), 'Add Student', self)
        add_student_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_student_action)

        about_action = QAction('About', self)
        help_menu_item.addAction(about_action)

        search_action = QAction(QIcon('icons/search.png'),'Search', self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(('Id', 'Name', 'Course', 'Mobile'))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addActions((add_student_action, search_action))

    def load_data(self):
        connection = sqlite3.connect('database.db')
        result = connection.execute("SELECT * FROM students")
        self.table.setRowCount(0)

        for number, row in enumerate(result):
            self.table.insertRow(number)
            for col_number, data in enumerate(row):
                self.table.setItem(number, col_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        self.dialog = SearchDialog()
        self.dialog.exec()


class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Insert Student Data')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        self.student_name.setPlaceholderText('Name')
        layout.addWidget(self.student_name)

        courses = ['Biology', 'Math', 'Chemistry', 'Physics']
        self.course_name = QComboBox()
        self.course_name.addItems(courses)
        layout.addWidget(self.course_name)

        self.student_phone = QLineEdit()
        self.student_phone.setPlaceholderText('Phone Number')
        layout.addWidget(self.student_phone)

        submit_button = QPushButton('Submit')
        submit_button.clicked.connect(self.add_student)
        layout.addWidget(submit_button)

        self.setLayout(layout)

    def add_student(self):
        name = self.student_name.text()
        course = self.course_name.itemText(self.course_name.currentIndex())
        mobile = self.student_phone.text()
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)',
                       (name, course, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        student.load_data()
        confirmation = QMessageBox.question(self, "Confirmation", "Do you want add another student?",
                                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if confirmation == QMessageBox.StandardButton.Yes:
            # Clear the input fields
            self.student_name.clear()
            self.student_phone.clear()

        elif confirmation == QMessageBox.StandardButton.No:
            self.accept()


class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Search Student')
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        self.student_name = QLineEdit()
        layout.addWidget(self.student_name)

        search_button = QPushButton('Search')
        search_button.clicked.connect(self.search_student)
        layout.addWidget(search_button)

        self.setLayout(layout)

    def search_student(self):
        name = self.student_name.text()
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        result = cursor.execute('SELECT * FROM students WHERE name = ?', (name,))
        rows = list(result)
        items = student.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            student.table.item(item.row(), 1).setSelected(True)

        cursor.close()
        connection.close()
        success_message = QMessageBox()
        success_message.setWindowTitle(f'{len(items)} Records Found')
        success_message.setText('This window will close automatically after 2 seconds')
        timer = QTimer(self)
        timer.timeout.connect(success_message.accept)
        timer.start(1500)
        success_message.exec()
        QTimer.singleShot(1000, self.accept)


app = QApplication(sys.argv)
student = MainWindow()
student.show()
student.load_data()
sys.exit(app.exec())
