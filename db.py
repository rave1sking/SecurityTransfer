import pymysql

class db():
  def __init__(self):
       self.conn = pymysql.connect(
            host='43.138.9.135',
            port=3306,
            user='liang',
            password='liangfengdi175x',
            db='file_sys',
            autocommit=True,
            charset='utf8'
            )
       self.cur = self.conn.cursor()