import socket
import ssl, threading, struct, json, os, pymysql

#打开数据库连接，这里是我的腾讯云服务器数据库
db = pymysql.connect(host= '43.138.9.135', port=3306, user='liang', passwd='liangfengdi175x', db='file_sys', charset='utf8')
#创建游标
cursor = db.cursor()
#查询版本
cursor.execute("select version()")
data = cursor.fetchone()
print("Data Version:" + str(data))

class server:
   def server_listen(self):
         #ssl的通用步骤
         #生成安全上下文
         context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
         #加载根证书
         context.load_verify_locations('./cer/ca/ca.crt')
         #加载服务器的证书和私钥
         context.load_cert_chain('./cer/server/server.crt', './cer/server/server-key.pem')
         #双向校验模式
         context.verify_mode = ssl.CERT_REQUIRED

         #监听与客户端通信的端口
         with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as sock: #param: 服务器之间的网络通信,#流式socket, 当使用TCP时选择此参数
                  sock.bind('',) #ip+端口
                  sock.listen(5)
                  with context.wrap_socket(sock, server_side = True) as ssl_sock: #在localhost上监听IPv4:
                  #with context.wrap_socket(sock, server_hostname=hostname) as ssock: #客户端
                       while True:
                           connection, addr = ssl_sock.accept() #接受客户端连接
                           print("Connected with", addr)
                           #分配进程
                           thread = threading.Thread(target = self.conn_thread, args = (connection,)) #args元组
                           #target is the callable object to be invoked by the run() method. Defaults to None, meaning nothing is called.
                           thread.start()
   def conn_thread(self, connection):
        while True:
             try:
                connection.settimeout(60)
                '''
                struct.calcsize(format)
                返回与格式字符串 format 相对应的结构的大小（亦即 pack(format, ...) 所产生的字节串对象的大小）。
                '''
                fileinfo_size = struct.calcsize('1024s')
                buf = connection.recv(fileinfo_size)

                if buf:
                    header_json = str(struct.unpack('1024s', buf)[0], encodings = 'utf-8').strip('\00')
                    header = json.load(header_json)
                    #Json转化成Python对象
                    #json.dump  python -> json
                    Command = header['Command']
                    #上传: 新建一个文件，然后写入
                    if Command == 'Upload':
                          fileName = header['fileName']
                          fileSize = header['fileSzie']
                          time = header['time']
                          user = header['user']
                          fileNewName = os.path.join('./ServerRec/', fileName)
                          print('Ready to upload: file new name is %s, filesize is %s' % (fileNewName, fileSize))
                          recvd_size = 0
                          file = open(fileNewName, 'wb')
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
                          print("Upload Over")
                          fileSize = float(fileSize)
                          if fileSize < 1024.0:
                              fileSize = "%s bytes" % (int(fileSize))
                          elif fileSize / 1024.0 <= 1024.0:
                              fileSize = "%.2f Kb" % (fileSize / 1024.0)
                          elif fileSize / 1024.0 / 1024.0 <= 1024.0:
                              fileSize = "%.2f Mb" % (fileSize / 1024.0 / 1024.0)
                          else:
                              fileSize = "%.2f Gb" % (fileSize / 1024.0 / 1024.0 / 1024.0)

                          uploadmsg = '{"文件名": "%s", "上传者": "%s", "上传时间": "%s", "大小": "%s"}\n' % \
                               (fileName, user, time, fileSize)
                          with open('./result.txt', 'a', encoding='utf-8') as list:
                                list.write(uploadmsg)

                          uploadlog = '\n%s upload a file "%s" at %s' % (user, fileName, time)
                          with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(uploadlog)
                    if Command == 'Login':
                         username = header['user']
                         password = header['password']
                         time = header['time']
                         sql = "select * from user where username == '%s' and password  '%s'" %(username, password)
                         cursor.execute(sql)
                         data = cursor.fetchone()
                         if data:
                            listResult = './result.txt'
                            header = {
                                'Aciton': 'Login',
                                'state': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                                #
                            }
                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s',header_hex)
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
                            with open('.\Serverlog.txt', 'a', encoding= 'utf-8') as list:
                                list.write(loginlog)
                         else:
                            header = {
                                 'Action': 'Login',
                                 'state': 'Fail',
                                 'fileSize': '',
                                 'user': username
                            }
                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                            loginlog = '\n%s try to login at "%s" , State: Fail ' % \
                                       (username, time)
                            with open('.\Serverlog.txt', 'a', encoding='utf-8') as list:
                                list.write(loginlog)
                    if Command == 'Download':
                        username = header['user']
                        password = header['password']
                        time = header['time']
                        sql = "select * from user where username = '%s' and password = '%s'" %(username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        filename = header['fileName']
                        if data: #登陆成功
                            filepath = os.path.join('./ServerRec/', filename)
                            header = {
                                'Action': 'Download',
                                'state': 'Success',
                                'fileSize': os.stat(filepath).st_size,
                                'user': username,
                            }

                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(filepath, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                            print('Send File Over')
                            downloadlog = '\n%s download a file "%s" at %s' %  (username, filename, time)
                            with open('/Serverlog.txt', 'a', encoding = 'utf-8') as list:
                                list.write(downloadlog)
                        else:
                            header = {
                                'Action': 'Download',
                                'state': 'Fail',
                                'fileSize': '',
                                'user': username
                            }

                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                    if Command == 'Update':
                        username = header['user']
                        password = header['password']
                        sql = "select * from user where username = '%s' and password = '%s'" % (username, password)
                        cursor.execute(sql)
                        data = cursor.fetchone()
                        if data: #返回文件列表
                            listResult = './result.txt'
                            header = {
                                'Action': 'Update',
                                'state': 'Success',
                                'fileSize': os.stat(listResult).st_size,
                                'user': username
                            }
                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)

                            fo = open(listResult, 'rb')
                            while True:
                                filedata = fo.read(1024)
                                if not filedata:
                                    break
                                connection.send(filedata)
                            fo.close()
                        else:
                            header = {
                                'Action': 'Update',
                                'state': 'Fail',
                                'fileSize': '',
                                'user': username
                            }
                            header_hex = bytes(json.dump(header).encode('utf-8'))
                            fhead = struct.pack('128s', header_hex)
                            connection.send(fhead)
                    # if Command == 'Register':
                    #     username = header['user']
                    #     password = header['password']
                    #     time = header['time']
                    #     sql = "select * from user where username = '%s'" % (username)
                    #     cursor.execute(sql)
                    #     data = cursor.fetchone()
                    #     if data:
                    #         # 定义文件头信息，包含文件名和文件大小
                    #         header = {
                    #             'Feedback': 'Register',
                    #             'stat': 'Exist',
                    #             'fileSize': '',
                    #             'user': username
                    #         }
                    #         header_hex = bytes(json.dumps(header).encode('utf-8'))
                    #         fhead = struct.pack('128s', header_hex)
                    #         connection.send(fhead)
                    #         loginlog = loginlog = '\n%s try to register at "%s" , Stat: Fail ,Username already be used' % \
                    #                    (username, time)
                    #         with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                    #             list.write(loginlog)
                    #     else:
                    #         sql = "insert into user values ('','%s','%s')"%(username,password)
                    #         cursor.execute(sql)
                    #         db.commit()
                    #         # 定义文件头信息，包含文件名和文件大小
                    #         header = {
                    #             'Feedback': 'Register',
                    #             'stat': 'Success',
                    #             'fileSize': '',
                    #             'user': username
                    #         }
                    #         header_hex = bytes(json.dumps(header).encode('utf-8'))
                    #         fhead = struct.pack('128s', header_hex)
                    #         connection.send(fhead)
                    #         loginlog = '\n%s try to register at "%s" , Stat: Success ' % \
                    #                    (username, time)
                    #         with open('./Serverlog.txt', 'a', encoding='utf-8') as list:
                    #             list.write(loginlog)
                    if Command == 'Register':
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
                            loginlog = loginlog = '\n%s try to register at "%s" , Stat: Fail ,Username already be used' % \
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
    server = server()
    server.server_listen()








