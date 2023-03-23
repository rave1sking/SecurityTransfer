from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QTableView, QApplication

results = [{'filename': '318照片.zip', 'size': '48.86 Mb', 'uploader': 'liang', 'upload_time': '2023-03-22 19:43:21'}]

# Create a QStandardItemModel and set column headers
model = QStandardItemModel()
model.setHorizontalHeaderLabels(['文件名', '大小', '上传者', '上传时间'])

# Add data to QStandardItemModel
for row_num, row_data in enumerate(results):
    for col_num, col_name in enumerate(['filename', 'size', 'uploader', 'upload_time']):
        item = QStandardItem(row_data[col_name])
        model.setItem(row_num, col_num, item)

# Create a QTableView and set QStandardItemModel as its model
table = QTableView()
table.setModel(model)

# Set table properties
table.setSortingEnabled(True)
table.horizontalHeader().setStretchLastSection(True)
table.verticalHeader().setVisible(False)

# Show the table
app = QApplication([])
table.show()
app.exec_()