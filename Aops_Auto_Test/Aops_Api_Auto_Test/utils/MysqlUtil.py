import pymysql
import pymysql.cursors
from .LogUtil import my_log
from ..config.conf import ConfigYaml


class Mysql(object):

    def __init__(self,host, user, database, port):
        self.log = my_log()
        self.host=host
        self.user=user
        self.database=database
        # self.charset=charset
        self.port=port

    def connect(self):
        self.conn = pymysql.connect(host=self.host, user=self.user,database=self.database,port=self.port)
        self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
        return self.cursor

    def fetchone(self, sql):
        """
        查询单个数据
        :param sql:
        :return:
        """
        self.cursor.execute(sql)
        return self.cursor.fetchone()

    def fetchall(self, sql):
        """
        查询所有数据
        :param sql:
        :return:
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def exec(self, sql):
        """
        执行sql语句
        :return:
        """
        try:
            if self.conn and self.cursor:
                self.cursor.execute(sql)
                self.conn.commit()
        except Exception as ex:
            self.conn.rollback()
            self.log.error("Mysql 执行失败")
            self.log.error(ex)
            return False
        return True

    def close(self):
        self.cursor.close()
        self.conn.close()


host = ConfigYaml().get_db_config_info()['host']
user = ConfigYaml().get_db_config_info()['user']
database = ConfigYaml().get_db_config_info()['database']
port = ConfigYaml().get_db_config_info()['port']
ql = Mysql(host, user, database, int(port))



