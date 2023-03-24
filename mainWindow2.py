# -*- coding: utf-8 -*-
import sys
import threading

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import qdarkstyle
from client import *
class MainWindow(QWidget):
    def __init__(self, username, password):
        super(MainWindow, self).__init__()
        self.resize(1200, 900)
        self.setWindowTitle("欢迎使用安全文件传输系统")
        # 查询模型
        self.queryModel = None
        # 数据表
        self.tableView = None
        # 当前页
        self.currentPage = 1
        # 总页数
        self.totalPage = 1
        # 总记录数
        self.totalRecord = 0
        # 每页数据数
        self.pageRecord = 10

        self.client = client_ssl()
        self.client.login(username, password)
        self.username = username
        self.password = password
        self.setUpUI()


    def setUpUI(self):
        self.layout = QVBoxLayout()
        self.Hlayout1 = QHBoxLayout()
        self.Hlayout2 = QHBoxLayout()

        # Hlayout1控件的初始化
        self.FileNamelabel = QLabel(self)
        self.FileNamelabel.setFixedHeight(32)
        font = QFont()
        font.setPixelSize(15)
        self.FileNamelabel.setFont(font)

        self.chooseButton = QPushButton("选择文件")
        self.chooseButton.setFixedHeight(32)
        self.chooseButton.setFont(font)

        self.chooseButton.clicked.connect(self.openfile)



        self.UploadButton = QPushButton("上传文件")
        self.UploadButton.setFixedHeight(32)
        self.UploadButton.setFont(font)
        self.UploadButton.clicked.connect(self.uploadfile)



        self.Hlayout1.addWidget(self.FileNamelabel)
        self.Hlayout1.addWidget(self.chooseButton)
        self.Hlayout1.addWidget(self.UploadButton)

        # Hlayout2初始化
        self.jumpToLabel = QLabel("跳转到第")
        self.pageEdit = QLineEdit()
        self.pageEdit.setFixedWidth(30)
        s = "/" + str(self.totalPage) + "页"
        self.pageLabel = QLabel(s)
        self.jumpToButton = QPushButton("跳转")
        self.prevButton = QPushButton("前一页")
        self.prevButton.setFixedWidth(60)
        self.backButton = QPushButton("后一页")
        self.backButton.setFixedWidth(60)

        Hlayout = QHBoxLayout()
        Hlayout.addWidget(self.jumpToLabel)
        Hlayout.addWidget(self.pageEdit)
        Hlayout.addWidget(self.pageLabel)
        Hlayout.addWidget(self.jumpToButton)
        Hlayout.addWidget(self.prevButton)
        Hlayout.addWidget(self.backButton)
        widget = QWidget()
        widget.setLayout(Hlayout)
        widget.setFixedWidth(300)
        self.Hlayout2.addWidget(widget)

        # tableView
        self.results = []

        self.model = QStandardItemModel(len(self.results),4)
        self.model.setHorizontalHeaderLabels(['文件名', '上传者', '时间', '文件大小'])
        self.file_list = open('./ClientCache/file_list.txt', 'rb')

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tableView.clicked.connect(self.on_item_clicked)
        #index = self.tableView.currentIndex()


        # for row_num, row_data in enumerate(self.results):
        #     for idx, item in enumerate(row_data):
        #         qitem = QStandardItem(item)
        #         self.model.setItem(row_num, idx, qitem)
        # self.results = []

        self.tableView.setModel(self.model)

        self.UpdateButton = QPushButton("更新文件列表")
        self.UpdateButton.setFixedHeight(32)
        self.UpdateButton.setFont(font)
        self.UpdateButton.clicked.connect(self.updatefile)

        self.DownloadButton = QPushButton("下载文件")
        self.DownloadButton.setFixedHeight(32)
        self.DownloadButton.setFont(font)
        self.DownloadButton.clicked.connect(self.download)

        self.Hlayout3 = QHBoxLayout()
        self.Hlayout3.addWidget(self.UpdateButton)
        self.Hlayout3.addWidget(self.DownloadButton)

        self.layout.addLayout(self.Hlayout1)
        self.layout.addWidget(self.tableView)
        #self.layout.addLayout()
        self.layout.addLayout(self.Hlayout2)
        self.layout.addLayout(self.Hlayout3)

        self.setLayout(self.layout)

        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)

    def setButtonStatus(self):
        if(self.currentPage==self.totalPage):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(False)
        if(self.currentPage==1):
            self.backButton.setEnabled(True)
            self.prevButton.setEnabled(False)
        if(self.currentPage<self.totalPage and self.currentPage>1):
            self.prevButton.setEnabled(True)
            self.backButton.setEnabled(True)

    # 得到记录数

    def getTotalRecordCount(self):
            self.totalRecord = len(self.results)
            return


    # 得到总页数
    def getPageCount(self):
        self.getTotalRecordCount()
        # 上取整
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        return

    # 向前翻页
    def prevButtonClicked(self):
        self.currentPage -= 1
        if (self.currentPage <= 1):
            self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        return

    # 向后翻页
    def backButtonClicked(self):
        self.currentPage += 1
        if (self.currentPage >= int(self.totalPage)):
            self.currentPage = int(self.totalPage)
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        return

    # 点击跳转
    def jumpToButtonClicked(self):
        if (self.pageEdit.text().isdigit()):
            self.currentPage = int(self.pageEdit.text())
            if (self.currentPage > self.totalPage):
                self.currentPage = self.totalPage
            if (self.currentPage <= 1):
                self.currentPage = 1
        else:
            self.currentPage = 1
        index = (self.currentPage - 1) * self.pageRecord
        self.pageEdit.setText(str(self.currentPage))
        return

    def openfile(self):
        openfile_name = QFileDialog.getOpenFileName(self,'选择文件','/','')
        self.Filename = openfile_name[0]
        if self.Filename:
            self.FileNamelabel.setText(self.Filename)
    def uploadfile(self):
        thread = threading.Thread(target=self.client.upload, args=(self.Filename,self.username, self.password))
        thread.start()
        print(QMessageBox.information(self, "提示", "上传成功!", QMessageBox.Yes, QMessageBox.Yes))
    def updatefile(self):
        # 获得Server端result.txt的内容,写入file_list.txt的内容，展示到QTableView中
        thread = threading.Thread(target=self.client.update, args=(self.username, self.password))
        thread.start()

        with open('./ClientCache/result.txt', 'r', encoding='utf-8') as f:
            for line in f:
                # Parse the JSON object
                # Extract the fields using regular expressions
                filename = re.search(r'"文件名":\s*"(.+?)"', line).group(1)
                uploader = re.search(r'"上传者":\s*"(.+?)"', line).group(1)
                upload_time = re.search(r'"上传时间":\s*"(.+?)"', line).group(1)
                size = re.search(r'"大小":\s*"(.+?)"', line).group(1)
                self.results.append([filename, uploader, upload_time, size])
        for row_num, row_data in enumerate(self.results):
            for idx, item in enumerate(row_data):
                qitem = QStandardItem(item)
                self.model.setItem(row_num, idx, qitem)
        self.results = []
        QApplication.processEvents()
        print(QMessageBox.information(self, "提示", "更新服务端文件列表成功!", QMessageBox.Yes, QMessageBox.Yes))
    def on_item_clicked(self, index):
        # 获取被点击的 item 的行、列和数据
        row = index.row()
        col = index.column()
        item = self.model.item(row, col)
        self.data = item.data(Qt.DisplayRole)

        print(f"Item clicked: row {row}, col {col}, data '{self.data}'")
    def download(self):
         file_name = self.data
         thread = threading.Thread(target=self.client.download, args=(file_name,self.username, self.password))
         thread.start()
         print(QMessageBox.information(self, "提示", "下载成功!", QMessageBox.Yes, QMessageBox.Yes))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = MainWindow('1', 'c4ca4238a0b923820dcc509a6f75849b')
    mainMindow.show()
    sys.exit(app.exec_())
