# -*- coding: utf-8 -*-
import sys
import threading
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt
import qdarkstyle
from PyQt5.QtSql import *
from client import *
import json
import re


class BookStorageViewer(QWidget):
    def __init__(self):
        super(BookStorageViewer, self).__init__()
        self.resize(1200, 900)
        self.setWindowTitle("欢迎使用安全文件传输系统")
        # 查询模型
        self.queryModel = None
        # 数据表
        self.tableView = None
        # 当前页
        self.currentPage = 0
        # 总页数
        self.totalPage = 0
        # 总记录数
        self.totalRecord = 0
        # 每页数据数
        self.pageRecord = 10
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

        self.searchEdit = QLineEdit()
        self.searchEdit.setFixedHeight(32)
        font = QFont()
        font.setPixelSize(15)
        self.searchEdit.setFont(font)

        self.searchButton = QPushButton("上传")
        self.searchButton.setFixedHeight(32)
        self.searchButton.setFont(font)
        self.searchButton.setIcon(QIcon(QPixmap("./images/search.png")))

        self.searchButton.clicked.connect(self.openfile)



        # self.condisionComboBox = QComboBox()
        # searchCondision = ['按书名查询', '按书号查询', '按作者查询', '按分类查询', '按出版社查询']
        # self.condisionComboBox.setFixedHeight(32)
        # self.condisionComboBox.setFont(font)
        # self.condisionComboBox.addItems(searchCondision)

        self.Hlayout1.addWidget(self.searchEdit)
        self.Hlayout1.addWidget(self.searchButton)
        #self.Hlayout1.addWidget(self.condisionComboBox)


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
        self.n = len(self.results)

        self.model = QStandardItemModel(self.n, 4)
        self.model.setHorizontalHeaderLabels(['文件名', '上传者', '文件大小', '时间'])

        # with open('./ClientCache/result.txt', 'r', encoding='utf-8') as f:
        #     for line in f:
        #         # Parse the JSON object
        #         obj = json.loads(line)
        #         # Extract the fields using regular expressions
        #         filename = re.search(r'"文件名":\s*"(.+?)"', line).group(1)
        #         uploader = re.search(r'"上传者":\s*"(.+?)"', line).group(1)
        #         upload_time = re.search(r'"上传时间":\s*"(.+?)"', line).group(1)
        #         size = re.search(r'"大小":\s*"(.+?)"', line).group(1)
        #         self.results.append({filename, uploader, upload_time, size})
        # for row_num, row_data in enumerate(self.results):
        #     for idx, item in enumerate(row_data):
        #         qitem = QStandardItem(item)
        #         self.model.setItem(row_num, idx, qitem)


        # 序号，文件名，上传用户，大小，上传时间，库存，剩余可借
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName('./db/LibraryManagement.db')
        self.db.open()

        self.tableView = QTableView()
        self.tableView.horizontalHeader().setStretchLastSection(True)
        self.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)

        #self.searchButtonClicked()
        self.tableView.setModel(self.model)

        self.UpdateButton = QPushButton("更新文件列表")
        self.UpdateButton.setFixedHeight(32)
        self.UpdateButton.setFont(font)
        self.UpdateButton.clicked.connect(self.updatefile)

        self.Hlayout3 = QHBoxLayout()
        self.Hlayout3.addWidget(self.UpdateButton)

        self.layout.addLayout(self.Hlayout1)
        self.layout.addWidget(self.tableView)
        #self.layout.addLayout()
        self.layout.addLayout(self.Hlayout2)
        self.layout.addLayout(self.Hlayout3)

        self.setLayout(self.layout)

        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)

        self.queryModel = QSqlQueryModel()
        self.searchButtonClicked()
        self.tableView.setModel(self.queryModel)

        self.queryModel.setHeaderData(0, Qt.Horizontal, "书名")
        self.queryModel.setHeaderData(1, Qt.Horizontal, "书号")
        self.queryModel.setHeaderData(2, Qt.Horizontal, "作者")
        self.queryModel.setHeaderData(3, Qt.Horizontal, "分类")
        self.queryModel.setHeaderData(4, Qt.Horizontal, "出版社")
        self.queryModel.setHeaderData(5, Qt.Horizontal, "出版时间")
        self.queryModel.setHeaderData(6, Qt.Horizontal, "库存")
        self.queryModel.setHeaderData(7, Qt.Horizontal, "剩余可借")
        self.queryModel.setHeaderData(8, Qt.Horizontal, "总借阅次数")

        self.layout.addLayout(self.Hlayout1)
        self.layout.addWidget(self.tableView)
        self.layout.addLayout(self.Hlayout2)
        self.setLayout(self.layout)
        self.searchButton.clicked.connect(self.searchButtonClicked)
        self.prevButton.clicked.connect(self.prevButtonClicked)
        self.backButton.clicked.connect(self.backButtonClicked)
        self.jumpToButton.clicked.connect(self.jumpToButtonClicked)
        self.searchEdit.returnPressed.connect(self.searchButtonClicked)


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



    # 得到总页数


    # 分页记录查询


    def getTotalRecordCount(self):
        self.queryModel.setQuery("SELECT * FROM Book")
        self.totalRecord = self.queryModel.rowCount()
        return

    # 得到总页数
    def getPageCount(self):
        self.getTotalRecordCount()
        # 上取整
        self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        return

    # 分页记录查询
    def recordQuery(self, index):
        queryCondition = ""
        # conditionChoice = self.condisionComboBox.currentText()
        # if (conditionChoice == "按书名查询"):
        #     conditionChoice = 'BookName'
        # elif (conditionChoice == "按书号查询"):
        #     conditionChoice = 'BookId'
        # elif (conditionChoice == "按作者查询"):
        #     conditionChoice = 'Auth'
        # elif (conditionChoice == '按分类查询'):
        #     conditionChoice = 'Category'
        # else:
        #     conditionChoice = 'Publisher'

        # if (self.searchEdit.text() == ""):
        #     queryCondition = "select * from Book"
        #     self.queryModel.setQuery(queryCondition)
        #     self.totalRecord = self.queryModel.rowCount()
        #     self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        #     label = "/" + str(int(self.totalPage)) + "页"
        #     self.pageLabel.setText(label)
        #     queryCondition = ("select * from Book ORDER BY %s  limit %d,%d " % (conditionChoice,index, self.pageRecord))
        #     self.queryModel.setQuery(queryCondition)
        #     self.setButtonStatus()
        #     return
        #
        # # 得到模糊查询条件
        # temp = self.searchEdit.text()
        # s = '%'
        # for i in range(0, len(temp)):
        #     s = s + temp[i] + "%"
        # queryCondition = ("SELECT * FROM Book WHERE %s LIKE '%s' ORDER BY %s " % (
        #     conditionChoice, s,conditionChoice))
        # self.queryModel.setQuery(queryCondition)
        # self.totalRecord = self.queryModel.rowCount()
        # # 当查询无记录时的操作
        # if(self.totalRecord==0):
        #     print(QMessageBox.information(self,"提醒","查询无记录",QMessageBox.Yes,QMessageBox.Yes))
        #     queryCondition = "select * from Book"
        #     self.queryModel.setQuery(queryCondition)
        #     self.totalRecord = self.queryModel.rowCount()
        #     self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        #     label = "/" + str(int(self.totalPage)) + "页"
        #     self.pageLabel.setText(label)
        #     queryCondition = ("select * from Book ORDER BY %s  limit %d,%d " % (conditionChoice,index, self.pageRecord))
        #     self.queryModel.setQuery(queryCondition)
        #     self.setButtonStatus()
        #     return
        # self.totalPage = int((self.totalRecord + self.pageRecord - 1) / self.pageRecord)
        # label = "/" + str(int(self.totalPage)) + "页"
        # self.pageLabel.setText(label)
        # queryCondition = ("SELECT * FROM Book WHERE %s LIKE '%s' ORDER BY %s LIMIT %d,%d " % (
        #     conditionChoice, s, conditionChoice,index, self.pageRecord))
        # self.queryModel.setQuery(queryCondition)
        # self.setButtonStatus()
        # return

    # 点击查询
    def searchButtonClicked(self):
        self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        self.getPageCount()
        s = "/" + str(int(self.totalPage)) + "页"
        self.pageLabel.setText(s)
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return


    # 向前翻页
    def prevButtonClicked(self):
        self.currentPage -= 1
        if (self.currentPage <= 1):
            self.currentPage = 1
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
        return

    # 向后翻页
    def backButtonClicked(self):
        self.currentPage += 1
        if (self.currentPage >= int(self.totalPage)):
            self.currentPage = int(self.totalPage)
        self.pageEdit.setText(str(self.currentPage))
        index = (self.currentPage - 1) * self.pageRecord
        self.recordQuery(index)
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
        self.recordQuery(index)
        return

    def openfile(self):
        openfile_name = QFileDialog.getOpenFileName(self,'选择文件','/','')
        self.Filename = openfile_name[0]
        if self.Filename:
            self.FileNamelabel.setText(self.Filename)
    def uploadfile(self):
        client = client_ssl()
        client.login('liang','liang')
        print(self.Filename)
        thread = threading.Thread(target=client.upload, args=(self.Filename,'liang','liang'))
        #client.upload(self.Filename)
        print("Ready")
        thread.start()
    def updatefile(self):
        # 获得Server端result.txt的内容,写入file_list.txt的内容，展示到QTableView中
        client = client_ssl()
        client.login('liang', 'liang')
        thread = threading.Thread(target=client.update, args=('/ClientCache/result.txt','liang', 'liang'))
        thread.start()

        with open('./ClientCache/result.txt', 'r', encoding='utf-8') as f:
            for line in f:
                # Parse the JSON object
                obj = json.loads(line)
                # Extract the fields using regular expressions
                filename = re.search(r'"文件名":\s*"(.+?)"', line).group(1)
                uploader = re.search(r'"上传者":\s*"(.+?)"', line).group(1)
                upload_time = re.search(r'"上传时间":\s*"(.+?)"', line).group(1)
                size = re.search(r'"大小":\s*"(.+?)"', line).group(1)
                self.results.append({filename, uploader, upload_time, size})
        for row_num, row_data in enumerate(self.results):
            for idx, item in enumerate(row_data):
                qitem = QStandardItem(item)
                self.model.setItem(row_num, idx, qitem)
        QApplication.processEvents()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = BookStorageViewer()
    mainMindow.show()
    sys.exit(app.exec_())
