from django.db import connections
import base64
import re
import datetime
import decimal
import json


class RawSql:
    """Django原生sql操作数据库封装类"""
    __sql = ''
    __database_name = ''
    err_msg = ""

    @staticmethod
    def __doc__():
        """用户使用文档"""
        print("set_sql(sql_str)函数:设置sql参数\n"
              "查询类函数:\n"
              "get_dic(sql_str)函数:输出字典类型的查询结果\n"
              "get_list(sql_str)函数:返回列表型结果\n"
              "更新函数:\n"
              "execute(sql_str):传入sql语句，执行正确返回True，执行错误返回False\n"
              "set_db(self, database_name): 输入database的名字，重新设置操作数据库"
              "get_db(): 获取当前连接数据库")

    def __init__(self, database_name='default', sql=''):
        """构造函数"""
        self.__sql = sql
        self.__database_name = database_name
        self.__connection = connections[self.__database_name]

    def __del__(self):
        self.close()

    def set_db(self, database_name):
        self.__database_name = database_name

    def get_db(self):
        return self.__database_name

    def set_sql(self, sql):
        """set_sql(sql_str)函数:设置sql参数"""
        self.__sql = sql

    def get_json(self, sql='', parameters=None, blob=False):
        """get_dic(sql_str)函数"""
        if sql:
            self.__sql = sql
        if not self.__sql:
            print("没有SQL语句传入\n")
            return False
        cursor = self.__connection.cursor()
        try:
            if parameters:
                cursor.execute(self.__sql, parameters)
            else:
                cursor.execute(self.__sql)
        except Exception as e:
            self.err_msg = str(e)
        columns = [col[0] for col in cursor.description]
        get_sql_data = cursor.fetchall()
        if not get_sql_data:
            return None
        lists = []
        for row in get_sql_data:
            if blob:  # 是否有lob
                row = [r for r in row]  # tuple 转 list
                for idx, b in enumerate(row):
                    if bool(re.search("lob|LOB", str(type(b)))):
                        row[idx] = str(base64.b64encode(b.read()), 'utf-8')
            datetime_val = re.search(r'datetime.datetime\(.*\)', str(row))
            datetime_timedelta = re.search(r'datetime.time\(.*\)', str(row))
            decimal_val = re.search(r'Decimal\(.*\)', str(row))
            if datetime_val or decimal_val or datetime_timedelta:
                lists.append(dict(zip(columns, [self.type_analyst(var) for var in row])))
            else:
                lists.append(dict(zip(columns, row)))
        result = str(lists).replace('\'', '\"')
        result = result.replace('"[', '[')
        result = result.replace(']"', ']')
        result = result.replace("None", '""')
        return result

    @staticmethod
    def type_analyst(value):
        if isinstance(value, datetime.datetime):
            return str(value)
        if isinstance(value, datetime.time):
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

    def get_list(self, sql='', parameters=None, result_type='row'):
        """get_list(sql_str)函数"""
        if sql:
            self.__sql = sql
        if not self.__sql:
            print("没有SQL语句传入\n")
            return False
        cursor = self.__connection.cursor()
        try:
            if parameters:
                cursor.execute(self.__sql, parameters)
            else:
                cursor.execute(self.__sql)
        except Exception as e:
            self.err_msg = str(e)
            print(self.err_msg)
            return False
        data = cursor.fetchall()
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

    def execute(self, sql='', parameters=None):
        """执行增加，删除，修改操作，若成功则返回True, 失败则返回False"""
        if sql:
            self.__sql = sql
        if not self.__sql:
            print("没有SQL语句传入\n")
            self.err_msg = "没有SQL语句传入"
            return False
        cursor = self.__connection.cursor()
        try:
            if parameters:
                cursor.execute(self.__sql, parameters)
            else:
                cursor.execute(self.__sql)
            cursor.execute('commit')
            return True
        except Exception as e:
            connections[self.__database_name].rollback()
            self.err_msg = str(e)
            return False
        finally:
            cursor.close()

    def close(self):
        pass
        # self.__connection.close()

    def sql_bind(self, request, param='data', table=""):
        """
        构建根据请求自动绑定SQL
        主键可自增的只需要写字段名
        :param request:
        :param param:
        :param table:
        :return:
        """
        import json
        sql = "select column_name, data_type, data_length, nullable from user_tab_cols where Table_Name = '%s'" % table
        columns = self.get_json(sql)
        columns = json.loads(columns)
        data = request.body.decode("utf-8")
        if data:
            data = json.loads(data)[param][0]
        else:
            return False
        new_dict = {}
        for i, j in data.items():
            new_dict[i.upper()] = j
        data = new_dict
        insert_columns = ""
        insert_values = ""
        for col in columns:
            col_name = col["COLUMN_NAME"]
            col_type = col["DATA_TYPE"]
            col_len = col["DATA_LENGTH"]
            col_null = col["NULLABLE"]
            if col_name not in data.keys() and col_null == "Y":
                continue
            else:
                try:
                    col_value = str(data[col_name])
                    if not col_value and col_null == "N":
                        raise Exception("字段\"%s\"不可为空" % col_name)
                except Exception:
                    raise Exception("字段\"%s\"不可为空" % col_name)
            if col_type == "VARCHAR2":
                if len(col_value) > int(col_len):
                    raise Exception("字段\"%s\"长度超出" % col_name)
            if col_type == "NUMBER" or col_type == "INTEGER":
                insert_values += col_value + ','
            else:
                insert_values += "'" + col_value + "'" + ','
            insert_columns += col_name + ','
        sql = r"insert into %s(%s) values(%s)" % (table, insert_columns[:-1], insert_values[:-1])
        return sql
