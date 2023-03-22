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