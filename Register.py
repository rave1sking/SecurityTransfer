import sys

import pymysql
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
from PyQt5.QtSql import *
import hashlib


class SignUpWidget(QWidget):
    student_signup_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setUpUI()

    def setUpUI(self):
        self.resize(800, 500)
        self.setWindowTitle("欢迎登陆文件传输系统")
        self.signUpLabel = QLabel("注   册")
        self.signUpLabel.setAlignment(Qt.AlignCenter)
        # self.signUpLabel.setFixedWidth(300)
        self.signUpLabel.setFixedHeight(100)
        font = QFont()
        font.setPixelSize(36)
        lineEditFont = QFont()
        lineEditFont.setPixelSize(16)
        self.signUpLabel.setFont(font)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.signUpLabel, Qt.AlignHCenter)
        self.setLayout(self.layout)
        # 表单，包括学号，姓名，密码，确认密码
        self.formlayout = QFormLayout()
        font.setPixelSize(18)
        # Row1
        # self.studentIdLabel = QLabel("id: ")
        # self.studentIdLabel.setFont(font)
        # self.studentIdLineEdit = QLineEdit()
        # self.studentIdLineEdit.setFixedWidth(180)
        # self.studentIdLineEdit.setFixedHeight(32)
        # self.studentIdLineEdit.setFont(lineEditFont)
        # self.studentIdLineEdit.setMaxLength(10)
        # self.formlayout.addRow(self.studentIdLabel, self.studentIdLineEdit)

        # Row
        self.UserNameLabel = QLabel("姓    名: ")
        self.UserNameLabel.setFont(font)
        self.UserNameLineEdit = QLineEdit()
        self.UserNameLineEdit.setFixedHeight(32)
        self.UserNameLineEdit.setFixedWidth(180)
        self.UserNameLineEdit.setFont(lineEditFont)
        self.UserNameLineEdit.setMaxLength(10)
        self.formlayout.addRow(self.UserNameLabel, self.UserNameLineEdit)

        lineEditFont.setPixelSize(10)

        # Row3
        self.passwordLabel = QLabel("密    码: ")
        self.passwordLabel.setFont(font)
        self.passwordLineEdit = QLineEdit()
        self.passwordLineEdit.setFixedWidth(180)
        self.passwordLineEdit.setFixedHeight(32)
        self.passwordLineEdit.setFont(lineEditFont)
        self.passwordLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordLineEdit.setMaxLength(16)
        self.formlayout.addRow(self.passwordLabel, self.passwordLineEdit)

        # Row
        self.passwordConfirmLabel = QLabel("确认密码: ")
        self.passwordConfirmLabel.setFont(font)
        self.passwordConfirmLineEdit = QLineEdit()
        self.passwordConfirmLineEdit.setFixedWidth(180)
        self.passwordConfirmLineEdit.setFixedHeight(32)
        self.passwordConfirmLineEdit.setFont(lineEditFont)
        self.passwordConfirmLineEdit.setEchoMode(QLineEdit.Password)
        self.passwordConfirmLineEdit.setMaxLength(16)
        self.formlayout.addRow(self.passwordConfirmLabel, self.passwordConfirmLineEdit)

        # Row5
        self.signUpbutton = QPushButton("注 册")
        self.signUpbutton.setFixedWidth(120)
        self.signUpbutton.setFixedHeight(30)
        self.signUpbutton.setFont(font)
        self.formlayout.addRow("", self.signUpbutton)
        widget = QWidget()
        widget.setLayout(self.formlayout)
        widget.setFixedHeight(250)
        widget.setFixedWidth(300)
        self.Hlayout = QHBoxLayout()
        self.Hlayout.addWidget(widget, Qt.AlignCenter)
        widget = QWidget()
        widget.setLayout(self.Hlayout)
        self.layout.addWidget(widget, Qt.AlignHCenter)

        # 设置验证
        reg = QRegExp("PB[0~9]{8}")
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        # self.studentIdLineEdit.setValidator(pValidator)

        reg = QRegExp("[a-zA-z0-9]+$")
        pValidator.setRegExp(reg)
        self.passwordLineEdit.setValidator(pValidator)
        self.passwordConfirmLineEdit.setValidator(pValidator)
        self.signUpbutton.clicked.connect(self.SignUp)
        #self.studentIdLineEdit.returnPressed.connect(self.SignUp)
        self.UserNameLineEdit.returnPressed.connect(self.SignUp)
        self.passwordLineEdit.returnPressed.connect(self.SignUp)
        self.passwordConfirmLineEdit.returnPressed.connect(self.SignUp)

    def SignUp(self):

        UserName = self.UserNameLineEdit.text()
        password = self.passwordLineEdit.text()
        confirmPassword = self.passwordConfirmLineEdit.text()
        if (UserName == "" or password == "" or confirmPassword == ""):
            print(QMessageBox.warning(self, "警告", "表单不可为空，请重新输入", QMessageBox.Yes, QMessageBox.Yes))
            return
        else:  # 需要处理逻辑，1.账号已存在;2.密码不匹配;3.插入user表
            self.conn = pymysql.connect(
                host = '43.138.9.135',
                port=3306,
                user = 'liang',
                password = 'liangfengdi175x',
                db = 'file_sys',
                autocommit=True,
                charset = 'utf8'
            )
            self.cur = self.conn.cursor()
            if (confirmPassword != password):
                 print(QMessageBox.warning(self, "警告", "两次输入密码不一致，请重新输入", QMessageBox.Yes, QMessageBox.Yes))
                 return
            elif (confirmPassword == password):
                # md5编码
                hl = hashlib.md5()
                hl.update(password.encode(encoding='utf-8'))
                md5password = hl.hexdigest()
                sql = "SELECT * FROM t_user WHERE username='%s'" % (UserName)
                self.cur.execute(sql)
                # 有回显
                if (self.cur.fetchone()):
                     print(QMessageBox.warning(self, "警告", "该账号已存在,请重新输入", QMessageBox.Yes, QMessageBox.Yes))
                     return
                else:
                    sql = "INSERT INTO t_user(username, password) VALUES ('%s','%s')" % (
                    UserName,  md5password)
                    self.cur.execute(sql)
                    # self.cur.commit()
                print(QMessageBox.information(self, "提醒", "您已成功注册账号!", QMessageBox.Yes, QMessageBox.Yes))
                self.student_signup_signal.emit(UserName)
                self.cur.close()
                return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = SignUpWidget()
    mainMindow.show()
    sys.exit(app.exec_())