import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import qdarkstyle
import hashlib
from PyQt5.QtSql import *
from db import *
import Register


class SignInWidget(QWidget):
    is_admin_signal = pyqtSignal()
    is_student_signal = pyqtSignal(str)
    #switch_window = QtCore.pyqtSignal()
    filename = './ClientCache/result.txt'
    results = []


    def __init__(self):
        super(SignInWidget, self).__init__()
        self.resize(900, 600)
        self.setWindowTitle("用户登录")
        self.setUpUI()

    def setUpUI(self):
        self.Vlayout = QVBoxLayout(self)
        self.Hlayout1 = QHBoxLayout()
        self.Hlayout2 = QHBoxLayout()
        self.formlayout = QFormLayout()


        labelFont = QFont()
        labelFont.setPixelSize(18)

        lineEditFont = QFont()
        lineEditFont.setPixelSize(16)

        self.label1 = QLabel("账号: ")
        self.label1.setFont(labelFont)
        self.lineEdit1 = QLineEdit()
        self.lineEdit1.setFixedHeight(32)
        self.lineEdit1.setFixedWidth(180)
        self.lineEdit1.setFont(lineEditFont)
        self.lineEdit1.setMaxLength(10)

        self.formlayout.addRow(self.label1, self.lineEdit1)

        self.label2 = QLabel("密码: ")
        self.label2.setFont(labelFont)
        self.lineEdit2 = QLineEdit()
        self.lineEdit2.setFixedHeight(32)
        self.lineEdit2.setFixedWidth(180)
        self.lineEdit2.setMaxLength(16)

        # 设置验证
        reg = QRegExp("[a-zA-z0-9]+$")
        pValidator = QRegExpValidator(self)
        pValidator.setRegExp(reg)
        self.lineEdit1.setValidator(pValidator)
        self.lineEdit2.setValidator(pValidator)

        passwordFont = QFont()
        passwordFont.setPixelSize(10)
        self.lineEdit2.setFont(passwordFont)

        self.lineEdit2.setEchoMode(QLineEdit.Password)
        self.formlayout.addRow(self.label2, self.lineEdit2)


        self.signIn = QPushButton("登 录")
        self.signIn.setFixedWidth(80)
        self.signIn.setFixedHeight(30)
        self.signIn.setFont(labelFont)
        #self.formlayout.addRow(self.Register, self.signIn)

        # self.label3 = QLabel("还没有账号?")
        # self.label3.setFont(labelFont)

        self.Register = QPushButton("注册")
        self.Register.setFixedWidth(80)
        self.Register.setFixedHeight(30)
        self.Register.setFont(labelFont)

        self.formlayout.addRow(self.signIn, self.Register)

        #self.formlayout.addRow(self.label3,self.Register)



        self.label = QLabel("欢迎使用安全文件传输系统")
        fontlabel = QFont()
        fontlabel.setPixelSize(30)
        self.label.setFixedWidth(390)
        # self.label.setFixedHeight(80)
        self.label.setFont(fontlabel)
        self.Hlayout1.addWidget(self.label, Qt.AlignCenter)
        self.widget1 = QWidget()
        self.widget1.setLayout(self.Hlayout1)
        self.widget2 = QWidget()
        self.widget2.setFixedWidth(300)
        self.widget2.setFixedHeight(150)
        self.widget2.setLayout(self.formlayout)
        self.Hlayout2.addWidget(self.widget2, Qt.AlignCenter)
        self.widget = QWidget()
        self.widget.setLayout(self.Hlayout2)
        self.Vlayout.addWidget(self.widget1)
        self.Vlayout.addWidget(self.widget, Qt.AlignTop)

        self.signIn.clicked.connect(self.signInCheck)
        self.Register.clicked.connect(self.go_to_reg)
        self.lineEdit2.returnPressed.connect(self.signInCheck)
        self.lineEdit1.returnPressed.connect(self.signInCheck)



    def signInCheck(self):
        UserName = self.lineEdit1.text()
        password = self.lineEdit2.text()
        if (UserName == "" or password == ""):
            print(QMessageBox.warning(self, "警告", "账号和密码不可为空!", QMessageBox.Yes, QMessageBox.Yes))
            return
        # 打开数据库连接
        self.database = db()
        self.conn = self.database.conn
        self.cur = self.database.cur
        sql = "SELECT * FROM t_user WHERE username ='%s'" % (UserName)
        self.cur.execute(sql)
        #self.cur.close()

        hl = hashlib.md5()
        hl.update(password.encode(encoding='utf-8'))
        res = self.cur.fetchone()
        print(res)
        if UserName == res[1]:
            print("1 match")
        if hl.hexdigest() == res[2]:
            print("2 match")
        if (not res):
            print(QMessageBox.information(self, "提示", "该账号不存在!", QMessageBox.Yes, QMessageBox.Yes))
        else:

            if (UserName == res[1] and hl.hexdigest() == res[2]):
                # 如果是管理员
                # if (query.value(3)==1):
                #     self.is_admin_signal.emit()
                # else:
                #     self.is_student_signal.emit(studentId)
                self.go_to_reg()
            else:
                print(QMessageBox.information(self, "提示", "密码错误!", QMessageBox.Yes, QMessageBox.Yes))
        self.cur.close()
        return
    def go_to_reg(self):
        self.reg_window = Register.SignUpWidget()
        self.reg_window.show()
        self.hide()
    #def go_to_main(self):


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("./images/MainWindow_1.png"))
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = SignInWidget()
    mainMindow.show()
    sys.exit(app.exec_())