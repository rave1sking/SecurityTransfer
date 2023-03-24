import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableView, QAbstractItemView, QPushButton, QLabel, QSpinBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem

class Pagination(QWidget):
    def __init__(self, model, page_size=10, parent=None):
        super().__init__(parent)
        self.model = model
        self.page_size = page_size

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.layout.addWidget(self.table_view)

        self.control_panel = QWidget()
        self.control_layout = QVBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.prev_page)
        self.control_layout.addWidget(self.prev_button)
        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.control_layout.addWidget(self.next_button)
        self.page_label = QLabel()
        self.control_layout.addWidget(self.page_label)
        self.control_panel.setLayout(self.control_layout)
        self.layout.addWidget(self.control_panel)

        self.setLayout(self.layout)
        self.current_page = 0
        self.total_pages = (self.model.rowCount() - 1) // self.page_size + 1
        self.update_table()

    def update_table(self):
        self.table_view.clearSpans()
        start_index = self.current_page * self.page_size
        end_index = start_index + self.page_size

        for i in range(self.model.rowCount()):
            self.table_view.setRowHidden(i, i < start_index or i >= end_index)

        self.page_label.setText(f"Page {self.current_page + 1} of {self.total_pages}")
        self.prev_button.setDisabled(self.current_page == 0)
        self.next_button.setDisabled(self.current_page == self.total_pages - 1)

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_table()

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_table()


def main():
    app = QApplication(sys.argv)
    model = QStandardItemModel()
    model.setHorizontalHeaderLabels(["Name", "Age", "City"])
    for i in range(100):
        name = QStandardItem(f"Person {i + 1}")
        age = QStandardItem(f"{i % 50}")
        city = QStandardItem(f"City {i % 10}")
        model.appendRow([name, age, city])

    pagination = Pagination(model, page_size=10)
    pagination.show()

    sys.exit(app.exec_())
if __name__ == '__main__':
    main()