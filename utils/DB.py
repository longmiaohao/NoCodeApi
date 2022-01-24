import json
import os
import base64
import warnings
import re
import datetime
import decimal
import json


class DB:
    """
    身份识别
    """
    __username = ""
    __password = ""
    __sid = ""
    __host = ""
    __port = ""
    __err = ""
    __db_path = ""

    def __init__(self, *args):
        """
        构造函数：入参为1个的时候连接sqlite3
        :param args:
        self.__username = username
        self.__password = password
        self.__host = host
        self.__sid = sid
        self.__port = port
        self.__con = ""
        self.__cursor = ""
        self.err = ""
        """
        if len(args) == 1:
            self.__db_path = args[0]
        else:
            self.__username = args[0]
            self.__password = args[1]
            self.__host = args[2]
            self.__sid = args[3]
            self.__port = int(args[4])
        self.__con = ""
        self.__cursor = ""
        self.err = ""

    def connection_oracle(self):

        """
        oracle数据库连接
        :return:
        """
        os.environ["NLS_LANG"] = "SIMPLIFIED CHINESE_CHINA.UTF8"
        try:
            import cx_Oracle as cx  # oracle数据库驱动
            self.__con = cx.connect(self.__username, self.__password,
                                    self.__host + ':' + str(self.__port) + '/' + self.__sid)
            self.__cursor = self.__con.cursor()
            return self.__cursor
        except Exception as e:
            warnings.warn("Oracle数据库: " + self.__host + ":" + self.__port + " 连接失败\n" + str(e))
            print(str(e))
            self.err = str(e)
            return False

    def connection_sqlserver(self):
        # self.__con = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
        #             "Server=%s;"
        #             "Database=%s;"
        #             "Trusted_Connection=yes;"
        #             "uid=%s;pwd=%s" % (self.__host, self.__sid, self.__username, self.__password))
        try:
            import pymssql  # sqlserver数据库驱动 linux平台需要装freetsd依赖
            self.__con = pymssql.connect(host=self.__host, user=self.__username, password=self.__password, db=self.__sid, port=self.__port, charset='utf8')
            self.__cursor = self.__con.cursor()
            return self.__cursor
        except Exception as e:
            warnings.warn("sqlserver数据库: " + self.__host + ":" + self.__port + " 连接失败\n" + str(e))
            print(str(e))
            self.err = str(e)
            return False

    def connection_mysql(self):
        try:
            import pymysql
            self.__con = pymysql.connect(host=self.__host, user=self.__username, password=self.__password, database=self.__sid, port=self.__port, charset='utf8')
            self.__cursor = self.__con.cursor()
            return self.__cursor
        except Exception as e:
            # warnings.warn("mysql数据库: " + self.__host + ":" + self.__port + " 连接失败\n" + str(e))
            self.err = str(e)
            print(str(e))
            return False

    def connection_sqlite3(self):
        try:
            import sqlite3  # sqllite3数据库
            self.__con = sqlite3.connect(self.__db_path)
            self.__cursor = self.__con.cursor()
            return self.__cursor
        except Exception as e:
            warnings.warn("sqlite3数据库: 连接失败\n" + str(e))
            self.err = str(e)
            print(str(e))
            return False

    def get_json(self, sql='', parameters=None, blob=False):
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
        except Exception as e:
            warnings.warn("执行sql: " + sql + " error_msg:" + str(e))
            self.err = str(e)
            return None
        columns = [col[0] for col in self.__cursor.description]
        get_sql_data = self.__cursor.fetchall()
        if not get_sql_data:
            return None
        lists = []
        for row in get_sql_data:
            if blob:  # 是否有lob
                row = [r for r in row]  # tuple 转 list
                for idx, b in enumerate(row):
                    if bool(re.search("lob|LOB", str(type(b)))):
                        row[idx] = str(base64.b64encode(b.read()), 'utf-8')
            checkpoint = re.search(r'datetime.datetime\(.*\)', str(row))
            timedelta = re.search(r'datetime.timedelta\(.*\)', str(row))
            decimal_val = re.search(r'Decimal\(.*\)', str(row))
            double_quote = re.search(r'{\"', str(row))
            if checkpoint or timedelta or double_quote or decimal_val:
                lists.append(dict(zip(columns, [self.type_analyst(var) for var in row])))
            else:
                lists.append(dict(zip(columns, row)))
        result = str(lists).replace('\'', '"')
        result = result.replace('None', '""')
        return result

    @staticmethod
    def type_analyst(value):
        import datetime
        if isinstance(value, datetime.datetime):
            return str(value)
        if isinstance(value, datetime.timedelta):
            return str(value)
        if isinstance(value, decimal.Decimal):
            float_val = re.search(r'\d*\.\d+', str(value))
            if float_val:
                return float(float_val.group(0))
            else:
                return int(value)
        if re.search(r'{\"', str(value)):
            return json.loads(value)
        else:
            return value

    def execute(self, sql='', parameters=None):
        """执行增加，删除，修改操作，若成功则返回True, 失败则返回False"""
        if not sql:
            print("没有SQL语句传入\n")
            return False
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
            if not self.__db_path:
                self.__cursor.execute('commit')
            else:
                self.__con.commit()
            return True
        except Exception as e:
            self.err = str(e)
            warnings.warn(str(e))
            return False

    def get_list(self, sql='', parameters=None, result_type='row'):
        """get_list(sql_str)函数"""
        if parameters is None:
            parameters = []
        if not sql:
            print("没有SQL语句传入\n")
            return False
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
        except Exception as e:
            self.err = str(e)
            print(self.err)
            return False
        data = self.__cursor.fetchall()
        get_sql_data = []
        list_result = []
        if result_type == 'col':
            list_result = list(data)
        else:
            for tuple_var in data:
                for var in tuple_var:
                    get_sql_data.append(var)
                list_result += get_sql_data
                get_sql_data.clear()
        return list_result

    def close(self):
        try:
            self.__cursor.close()
            self.__con.close()
        except:
            pass

    def __del__(self):
        self.close()
