import re
import socket
import ssl,time,os,struct,json,tkinter

class client_ssl:
    def __init__(self):
        # 生成SSL上下文
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        # 加载信任根证书
        context.load_verify_locations('./cer/ca/ca.crt')
        # 加载客户端所用证书和私钥
        context.load_cert_chain('./cer/client/client.crt', './cer/client/client-key.pem')
        # 双向校验模式
        context.verify_mode = ssl.CERT_REQUIRED

        # 与服务端建立socket连接
        self.sock = socket.create_connection(('43.138.9.135', 9999))
        print("socket建立成功")
        # 将socket打包成SSL socket
        # 一定要注意的是这里的server_hostname是指服务端证书中设置的CN
        self.ssock = context.wrap_socket(self.sock, server_hostname='SERVER', server_side=False)

    def login(self,username,password):
        # 定义文件头信息，包含文件名和文件大小
        header = {
            'Command': 'Login',
            'fileName': '',
            'fileSize': '',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'user': username,
            'password': password,
        }
        print(header)
        header_hex = bytes(json.dumps(header).encode('utf-8'))
        fhead = struct.pack('1024s', header_hex)
        self.ssock.send(fhead)
        print('send over...')
        fileinfo_size = struct.calcsize('128s')
        buf = self.ssock.recv(fileinfo_size)
        if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            print(header_json)
            header = json.loads(header_json)
            stat = header['stat']
            if stat == 'Success':
                fileSize = header['fileSize']
                filenewname = os.path.join('./ClientCache/', 'result.txt')
                print('file new name is %s, filesize is %s' % (filenewname, fileSize))
                recvd_size = 0  # 定义接收了的文件大小
                file = open(filenewname, 'wb')
                print('start receiving...')
                while not recvd_size == fileSize:
                    if fileSize - recvd_size > 1024:
                        rdata = self.ssock.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = self.ssock.recv(fileSize - recvd_size)
                        recvd_size = fileSize
                    file.write(rdata)
                file.close()
                print('receive done')
                #self.ssock.close()
                return True

            else:
                return False

    def upload(self,filepath, username, password):
        if os.path.isfile(filepath):
            fileinfo_size = struct.calcsize('1024sl')  # 定义打包规则
            # 定义文件头信息，包含文件名和文件大小
            header = {
                'Command': 'Upload',
                'fileName': os.path.basename(filepath),
                'fileSize': os.stat(filepath).st_size,
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                'user': username,
                'password': password,
                'downloadFilename': '',
                'cookie': ''
            }
            print(header)
            header_hex = bytes(json.dumps(header).encode('utf-8'))
            fhead = struct.pack('1024s', header_hex)
            self.ssock.send(fhead)

            fo = open(filepath, 'rb')
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                self.ssock.send(filedata)
            fo.close()
            print('send over...')

            #tkinter.messagebox.showinfo('提示！', message='上传成功')
            #self.ssock.close()
        else:
            print('ERROR FILE')

    def download(self, filename):
        # 定义文件头信息，包含文件名和文件大小
        header = {
            'Command': 'Download',
            'fileName': filename,
            'fileSize': '',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'user': self.username,
            'password': self.password,
        }
        header_hex = bytes(json.dumps(header).encode('utf-8'))
        fhead = struct.pack('1024s', header_hex)
        self.ssock.send(fhead)

        fileinfo_size = struct.calcsize('128s')
        buf = self.ssock.recv(fileinfo_size)
        if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            print(header_json)
            header = json.loads(header_json)
            stat = header['stat']
            if stat == 'Success':
                fileSize = header['fileSize']
                filenewname = os.path.join('./ClientDownload/', filename)
                print('file new name is %s, filesize is %s' % (filenewname, fileSize))
                recvd_size = 0  # 定义接收了的文件大小
                file = open(filenewname, 'wb')
                print('start receiving...')
                while not recvd_size == fileSize:
                    if fileSize - recvd_size > 1024:
                        rdata = self.ssock.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = self.ssock.recv(fileSize - recvd_size)
                        recvd_size = fileSize
                    file.write(rdata)
                file.close()
                print('receive done')
                # self.ssock.close()
                tkinter.messagebox.showinfo('提示！',message='下载成功：' + filename)
                return True

            else:
                return False

    def update(self):
        # 定义文件头信息，包含文件名和文件大小
        header = {
            'Command': 'Update',
            'fileName': '',
            'fileSize': '',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'user': self.username,
            'password': self.password
        }
        header_hex = bytes(json.dumps(header).encode('utf-8'))
        fhead = struct.pack('1024s', header_hex)
        self.ssock.send(fhead)
        print('ask for updating...')
        fileinfo_size = struct.calcsize('128s')
        buf = self.ssock.recv(fileinfo_size)
        if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            print(header_json)
            header = json.loads(header_json)
            stat = header['stat']
            if stat == 'Success':
                fileSize = header['fileSize']
                filenewname = os.path.join('./ClientCache/', 'result.txt')
                print('file new name is %s, filesize is %s' % (filenewname, fileSize))
                recvd_size = 0  # 定义接收了的文件大小
                file = open(filenewname, 'wb')
                print('start receiving...')
                while not recvd_size == fileSize:
                    if fileSize - recvd_size > 1024:
                        rdata = self.ssock.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = self.ssock.recv(fileSize - recvd_size)
                        recvd_size = fileSize
                    file.write(rdata)
                file.close()
                print('receive done')


                # self.ssock.close()

    def register(self,username,password):
        # 定义文件头信息，包含文件名和文件大小
        header = {
            'Command': 'Register',
            'fileName': '',
            'fileSize': '',
            'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            'user': username,
            'password': password,
        }
        header_hex = bytes(json.dumps(header).encode('utf-8'))
        fhead = struct.pack('1024s', header_hex)
        self.ssock.send(fhead)
        print('Under registration...')
        fileinfo_size = struct.calcsize('128s')
        buf = self.ssock.recv(fileinfo_size)
        if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            print(header_json)
            header = json.loads(header_json)
            stat = header['stat']
            if stat == 'Success':
                return True

            else:
                return False


if __name__ == "__main__":
    client = client_ssl()
    filepath = ''
    client.login('liang','liang')
    client.upload(filepath)
import socket
import ssl, threading, struct, json, os, pymysql


#打开数据库连接
db = pymysql.connect(host= '43.138.9.135', port=3306, user='liang', passwd='liangfengdi175x', db='file_sys', charset='utf8')
#使用cursor方法创建一个游标
cursor = db.cursor()
#查询数据库版本
cursor.execute("select version()")
data = cursor.fetchone()
print(" Database Version:%s" % data)

class server_ssl:
    def server_listen(self):
        # 生成SSL上下文
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        #context = ssl._create_unverified_context()
        # 加载信任根证书
        context.load_verify_locations('./CA/ca.cer')
        # 加载服务器所用证书和私钥
        context.load_cert_chain('./CA/server.cer', './CA/server.key')
        # 双向校验模式
        context.verify_mode = ssl.CERT_REQUIRED

        # 监听端口
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock:
            sock.bind(('127.0.0.1', 9999))
            sock.listen(5)
            # 将socket打包成SSL socket
            with context.wrap_socket(sock, server_side=True) as ssock:
                while True:
                    # 接收客户端连接
                    print('Wating...')
                    connection, addr = ssock.accept()
                    print('Connected by ', addr)
                    #开启多线程,这里arg后面一定要跟逗号，否则报错
                    thread = threading.Thread(target=self.conn_thread, args=(connection,))
                    thread.start()

    def conn_thread(self,connection):
        while True:
            try:
                connection.settimeout(60)
                fileinfo_size = struct.calcsize('1024s')
                buf = connection.recv(fileinfo_size)
                if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
                    header_json = str(struct.unpack('1024s', buf)[0], encoding='utf-8').strip('\00')
                    #print(header_json)
                    header = json.loads(header_json)
                    Command = header['Command']

                    if Command == 'Upload':
                        fileName = header['fileName']
                        fileSize = header['fileSize']
                        time = header['time']
                        user = header['user']
                        filenewname = os.path.join('./ServerRec/', fileName)
                        print('Upload: file new name is %s, filesize is %s' % (filenewname, fileSize))
                        recvd_size = 0  # 定义接收了的文件大小
                        file = open(filenewname, 'wb')
                        print('start receiving...')
                        while not recvd_size == fileSize:
                            if fileSize - recvd_size > 1024:
                                rdata = connection.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = connection.recv(fileSize - recvd_size)
                                recvd_size = fileSize
                            file.write(rdata)
                        file.close()
                        print('receive done')

                        fileSize = float(fileSize)
                        if fileSize<1024.0:
                            fileSize = "%s bytes"%(int(fileSize))
                        elif fileSize/1024.0 <= 1024.0:
                            fileSize = "%.2f Kb"%(fileSize/1024.0)
                        elif fileSize/1024.0/1024.0 <= 1024.0:
                            fileSize = "%.2f Mb"%(fileSize/1024.0/1024.0)
                        else:
                            fileSize = "%.2f Gb"%(fileSize/1024.0/1024.0/1024.0)

                        uploadmsg = '{"文件名": "%s", "上传者": "%s", "上传时间": "%s", "大小": "%s"}\n'%\
                                    (fileName,user,time,fileSize)
                        with open('./result.txt','a',encoding='utf-8') as list:
                            list.write(uploadmsg)

                        uploadlog = '\n%s upload a file "%s" at %s' % \
                                        (user, fileName, time)
                        with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                            list.write(uploadlog)
                        #connection.close()

                    elif Command == 'Login':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s' and password = '%s'"%(username,password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            listResult = './result.txt'
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(listResult, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            print('%s login successfully')

                            loginlog = '\n%s try to login at "%s" , Stat: Success ' % \
                                        (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)
                            #connection.close()
                        else:
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Fail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to login at "%s" , Stat: Fail ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)

                    elif Command == 'Download':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s' and password = '%s'" % (username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        filename = header['fileName']
                        if data:

                            filepath = os.path.join('./ServerREc/', filename)
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Download',
                                'stat': 'Success',
                                'fileSize': os.stat(filepath).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(filepath, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            print('send file over...')
                            downloadlog = '\n%s download a file "%s" at %s' % \
                                          (username, filename, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(downloadlog)
                            # connection.close()
                        else:
                            header = {
                                'Feedback': 'Download',
                                'stat': 'LoginFail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                    elif Command == 'Update':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        sql = "select * from user where username = '%s' and password = '%s'" % (username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            listResult = './result.txt'
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Update',
                                'stat': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(listResult, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            #print('send list over...')
                            # connection.close()
                        else:
                            header = {
                                'Feedback': 'Login',
                                'stat': 'Fail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                    elif Command == 'Register':
                        # 查询数据表数据
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s'" % (username)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data:
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Register',
                                'stat': 'Exist',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to register at "%s" , Stat: Fail ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)
                        else:
                            sql = "insert into user values ('','%s','%s')"%(username,password)
                            cursor.execute(sql)
                            db.commit()
                            # 定义文件头信息，包含文件名和文件大小
                            header = {
                                'Feedback': 'Register',
                                'stat': 'Success',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dumps(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to register at "%s" , Stat: Success ' % \
                                       (username, time)
                            with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)

            except socket.timeout:
                connection.close()
                break
            except ConnectionResetError:
                connection.close()
                break

if __name__ == "__main__":
    server = server_ssl()
    server.server_listen()
