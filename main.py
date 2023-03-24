'''
Author: Fengdi Liang
Date: 2023/03/24
'''
import client_login
from client_login import  *

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    mainMindow = client_login.SignInWidget()
    mainMindow.show()
    sys.exit(app.exec_())


