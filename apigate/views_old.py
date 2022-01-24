from django.http import JsonResponse
from django.shortcuts import redirect, reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
from utils.DB import *
from utils.AES import *
import json
import time
import re
import urllib
from configparser import ConfigParser
import logging
from functools import wraps
import redis
from Privileges.PrivilegesWrapper import *


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config = ConfigParser()
# # 传入读取文件的地址，encoding文件编码格式，中文必须
config.read(os.path.join(BASE_DIR, "apigate", 'conf', 'api_conf.ini'), encoding='UTF-8')         # 当前工程下面 conf文件夹的script.ini
SECRET_KEY = config["SECRET_KEY"]["key"]
db_path = config["DB_PATH"]["path"]
# # 自定义日志文件
# logger = logging.getLogger(__name__)
# fh = logging.FileHandler(os.path.join(BASE_DIR, "apigate", "log", 'apicall.log'), encoding="utf-8")     # 当前工程下面 log文件夹的开交换机端口日志.log
# fh.setLevel(logging.ERROR)          # 设置日志等级
# formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
# fh.setFormatter(formatter)
# logger.addHandler(fh)


def create_table():
    """
    创建配置表
    字段：
    接口名： 255字符
    接口路径：url
    允许方式：GET POST ALL
    允许IP：
    目标数据库：TARGET_DB
    目标表或者视图：TARGET_TABLE_OR_VIEW
    执行SQL：EXECUTE_SQL
    :return:
    """
    db = DB(db_path)
    if not db.connection_sqlite3():
        warnings.warn("sqlite3数据库连接失败")
        return False
    sql = '''
        create table T_API_CONFIG(
            NAME nvarchar(255) not null primary key, -- comment '接口名称',
            URL varchar(255) unique , -- comment '部署地址',
            ALLOW_METHOD varchar(255) default 'GET', -- comment '允许方法GET POST ALL',
            ALLOW_IP varchar(255) default '*', -- comment '允许IP * 全部',
            TARGET_DB varchar(255) not null, -- comment '目标数据库',
            TARGET_TABLE_OR_VIEW varchar(255), -- comment '目标表或视图',
            EXECUTE_SQL varchar(3000), -- comment '自定义执行的SQL 优先级最高',
            RETURN_TARGET_TABLE_OR_VIEW varchar(3000) default '1' , -- comment '返回目标表或则视图信息',
            STATUS varchar(2) default '1', -- comment '启用状态',
            RETURN_FIELD varchar(2) default '0', -- comment '返回字段信息 如果是返回全表',
            RETURN_TOTAL varchar(2) default '0', -- comment '返回表记录数量',
            CREATE_TIME varchar(20), -- comment '创建时间',
            PER_PAGE varchar(20) default 'ALL', -- comment '每页记录条数',
            ALIAS_FIELDS varchar(1000), -- comment '字段别名',
            SORT varchar(1000), -- comment '排序',
            RETURN_FIELDS varchar(1000), -- comment '返回字段',
            INSERT_FIELDS varchar(1000), -- comment '插入字段',
            UPDATE_FIELDS varchar(1000), -- comment '修改字段',
            DELETE_FIELDS varchar(1000), -- comment '删除字段',
            DELETE_STATUS varchar(2), -- comment '删除状态',
            INSERT_STATUS varchar(2), -- comment '插入状态',
            UPDATE_STATUS varchar(2), -- comment '更新状态',
            `CONDITION` varchar(1000), -- comment '条件',
            CZLX varchar(2), -- comment '操作类型',
            CZSJ varchar(20) -- comment '操作时间'
        )
    '''
    db.execute(sql)
    sql = '''
        create table T_API_DATABASES(
            NAME nvarchar(255) not null primary key, -- comment '名称',
            TYPE varchar(255), -- comment '数据库类型',
            DB varchar(255), -- comment '数据库',
            IP varchar(255), -- comment '数据库IP',
            PORT varchar(255), -- comment '数据库端口',
            USERNAME varchar(255) not null, -- comment '用户名',
            PASSWORD varchar(255), -- comment '密码',
            CREATE_TIME varchar(20), -- comment '添加时间',
            STATUS varchar(2) default '1', -- comment '启用状态',
            CZLX varchar(2) default 'I', -- comment '操作类型',
            CZSJ varchar(20) -- comment '操作时间'
        )
    '''
    db.execute(sql)
    return True


def base(request):
    """
     默认首页
    :param request:
    :return:
    """
    # create_table()
    page = "home.html"
    base = 1
    return render(request, "base.html", locals())


def ApiConfig(request):
    """
    接口配置主页 新增，修改配置接口
    :param request:
    :return:
    """
    db = DB(db_path)
    db.connection_sqlite3()
    if request.method == "POST":
        name = request.POST.get("name", None)
        if not name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "名称不可为空"}, None)
        path = request.POST.get("path")
        if not path:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "路径不可为空"})
        allow_method = request.POST.get("allow_method")
        allow_ip = request.POST.get("allow_ip")
        db_name = request.POST.get("db")
        data_table = request.POST.get("data_table")
        sql = request.POST.get("sql", None)
        return_table = request.POST.get("return_table")
        per_page = request.POST.get("per_page")
        return_field_comment = request.POST.get("return_field_comment")
        return_total = request.POST.get("return_total")
        optype = request.POST.get("optype")
        insert_status = request.POST.get("insert_status")
        delete_status = request.POST.get("delete_status")
        update_status = request.POST.get("update_status")
        sort = request.POST.get("sort", None)
        if not db_name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "需要选择连接数据库"})
        if not sql and not data_table:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "需要选择连接数据表"})
        # sql校验
        if sql:
            db_info_sql = "select username, password, ip, db, port, type from T_API_DATABASES where name = '%s'" % db_name
            info = json.loads(db.get_json(db_info_sql))[0]
            test_db = DB(info["USERNAME"], Aes.decrypt(info["PASSWORD"], SECRET_KEY), info["IP"], info["DB"], info["PORT"])
            if info["TYPE"] == "Mysql":
                test_db.connection_mysql()
                test_db.get_json("select * from (%s) self_define_table" % sql.replace("&quto", "'"))
                test_db.close()
                if test_db.err:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "SQL检查不通过: %s" % test_db.err})
            elif info["TYPE"] == "Oracle":
                pass
            elif info["TYPE"] == "Sqlserver":
                pass
        try:
            if sort:
                json.loads(sort)
                sort = sort.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "排序JSON校验不通过"})
        condition = request.POST.get("condition")
        try:
            if condition:
                json.loads(condition)
                condition = condition.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件JSON校验不通过"})
        alias_fields = request.POST.get("alias_fields")
        try:
            if alias_fields:
                json.loads(alias_fields)
                alias_fields = alias_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "字段别名JSON校验不通过"})

        insert_fields = request.POST.get("insert_fields")
        try:
            if insert_fields:
                json.loads(insert_fields)
                insert_fields = insert_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "插入字段JSON校验不通过"})

        delete_fields = request.POST.get("delete_fields")
        try:
            if delete_fields:
                json.loads(delete_fields)
                delete_fields = delete_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除字段JSON校验不通过"})
        update_fields = request.POST.get("update_fields")
        try:
            if update_fields:
                json.loads(update_fields)
                update_fields = update_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新字段JSON校验不通过"})
        return_fields = request.POST.get("return_fields")
        try:
            if return_fields:
                json.loads(return_fields)
                return_fields = return_fields.replace('"', '\\"').upper()
        except:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "返回字段JSON校验不通过"})
        if sql:
            return_table = "0"
            return_field_comment = "0"
        status = request.POST.get("status")
        if optype == "add":
            sql = "insert into T_API_CONFIG(NAME, URL, ALLOW_METHOD, ALLOW_IP, TARGET_DB, TARGET_TABLE_OR_VIEW, " \
                  "EXECUTE_SQL, RETURN_TARGET_TABLE_OR_VIEW, STATUS, RETURN_FIELD, CREATE_TIME, PER_PAGE, SORT, " \
                  "CONDITION, ALIAS_FIELDS, INSERT_STATUS, UPDATE_STATUS, DELETE_STATUS, INSERT_FIELDS, UPDATE_FIELDS," \
                  " DELETE_FIELDS, RETURN_FIELDS, RETURN_TOTAL) " \
                  "values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s', '%s', '%s', '%s', '%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
                  (name, path, allow_method, allow_ip, db_name, data_table, sql, return_table, status, return_field_comment,
                   time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), per_page, sort, condition, alias_fields,
                   insert_status, update_status, delete_status, insert_fields, update_fields, delete_fields, return_fields, return_total)
            msg = "配置成功"
        else:
            sql = "update T_API_CONFIG set URL='%s', ALLOW_METHOD='%s', ALLOW_IP='%s', TARGET_DB='%s'," \
                  " TARGET_TABLE_OR_VIEW='%s', EXECUTE_SQL='%s', RETURN_TARGET_TABLE_OR_VIEW='%s', STATUS='%s', " \
                  "RETURN_FIELD='%s', CZLX='U', CZSJ='%s', PER_PAGE='%s', SORT='%s', CONDITION='%s', ALIAS_FIELDS='%s'," \
                  "INSERT_STATUS='%s', DELETE_STATUS='%s', UPDATE_STATUS='%s', INSERT_FIELDS='%s', DELETE_FIELDS='%s'," \
                  " UPDATE_FIELDS='%s', RETURN_FIELDS='%s', RETURN_TOTAL='%s'  where NAME='%s'" % \
                  (path, allow_method, allow_ip, db_name, data_table, sql, return_table, status, return_field_comment,
                  time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), per_page, sort, condition, alias_fields,
                   insert_status, delete_status, update_status, insert_fields, delete_fields, update_fields,
                   return_fields, return_total, name)
            msg = "修改成功"
        if db.execute(sql):
            return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg})
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": db.err})
    database_list = db.get_json("select name, db from T_API_DATABASES")
    if database_list:
        database_list = json.loads(database_list)
    else:
        database_list = []
    page = "ApiConfig.html"
    jiekou = 1
    return render(request, "base.html", locals())


def delete(request):
    name = request.GET.get("name", None)
    del_type = request.GET.get("del_type", None)
    if not name or not del_type:
        name = request.POST.get("name", None)
        del_type = request.POST.get("del_type", None)
    if not name or not del_type:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "参数不完整"},
                            safe=False, json_dumps_params={"ensure_ascii": False})
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    sql = ""
    if del_type == 'api':
        sql = "delete from T_API_CONFIG where name='%s'" % name
    if del_type == 'db':
        sql = "delete from T_API_DATABASES where name='%s'" % name
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": "01", "RTN_MSG": "删除成功"},
                            safe=False, json_dumps_params={"ensure_ascii": False})
    else:
        return JsonResponse({"RTN_CODE": "00", "RTN_MSG": "删除失败"},
                            safe=False, json_dumps_params={"ensure_ascii": False})


def ApiList(request):
    """
    获取配置接口列表 有name的时候为单一查询，用于修改
    :param request:
    :return:
    """
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    name = request.GET.get("name")
    if name:
        sql = "select a.NAME, a.URL, a.ALLOW_METHOD, a.ALLOW_IP, a.TARGET_DB, a.TARGET_TABLE_OR_VIEW, "\
            "a.EXECUTE_SQL, a.RETURN_TARGET_TABLE_OR_VIEW, a.STATUS, a.RETURN_FIELD, a.CREATE_TIME,"\
            "a.PER_PAGE, a.TARGET_DB TARGET_DB_NAME, a.CONDITION, a.SORT, a.ALIAS_FIELDS, a.RETURN_FIELDS,"\
            "a.INSERT_STATUS, a.DELETE_STATUS, a.UPDATE_STATUS, a.INSERT_FIELDS, a.DELETE_FIELDS, a.UPDATE_FIELDS,"\
            "a.RETURN_TOTAL, b.DB TARGET_DB from T_API_CONFIG a, "\
            "T_API_DATABASES b where a.TARGET_DB=b.NAME and a.NAME='%s'" % name
        db_list = sqlite3_db.get_json(sql)
    else:
        sql = "select NAME, URL, ALLOW_METHOD, ALLOW_IP, TARGET_DB, TARGET_TABLE_OR_VIEW, "\
              "EXECUTE_SQL, RETURN_TARGET_TABLE_OR_VIEW, STATUS, RETURN_FIELD, CREATE_TIME,"\
              "PER_PAGE,RETURN_FIELDS, RETURN_TOTAL from T_API_CONFIG"
        db_list = sqlite3_db.get_json(sql)
    if db_list:
        db_list = json.loads(db_list.replace('\\\\', '\\').replace('""""', '"{}"'))
    else:
        db_list = []
    if sqlite3_db.err:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})
    else:
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "查询成功", "DATA": db_list})


def GetTablesByDB(request):
    """
    通过数据库查询表
    :param request:
    :return:
    """
    name = request.POST.get("name")
    if not name:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "无参数"})
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    data = sqlite3_db.get_json("select * from T_API_DATABASES where name='%s'" % name)
    if data:
        data = json.loads(data)[0]
        username = data["USERNAME"]
        password = Aes.decrypt(data["PASSWORD"], SECRET_KEY)
        host = data["IP"]
        port = data["PORT"]
        db_name = data["DB"]
        db_type = data["TYPE"]
        db = DB(username, password, host, db_name, port)
        sql = ""
        if db_type == "Mysql":
            sql = "select TABLE_NAME, TABLE_COMMENT from information_schema.tables where TABLE_SCHEMA='%s'" % db_name
            if not db.connection_mysql():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        elif db_type == "Oracle":
            sql = "select TABLE_NAME, COMMENTS TABLE_COMMENT from user_tab_comments"
            if not db.connection_oracle():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        elif db_type == "Sqlserver":
            sql = "select t1.name TABLE_NAME, t2.VALUE TABLE_COMMENT from (select name, id from sysobjects where " \
                  "xtype = 'u' and name != 'sysdiagrams') t1 LEFT JOIN " \
                  "(select value, major_id from sys.extended_properties ex_p where ex_p.minor_id=0)" \
                  " t2 on t1.id=t2.major_id"
            if not db.connection_sqlserver():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库连接失败"})
        data = db.get_json(sql)
        if data:
            data = json.loads(data)
        else:
            data = []
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "查询成功", "DATA": data})
    else:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库没有配置"})


@require_http_methods(["POST"])
def TestConnection(request):
    """
    数据库连接测试
    :param request:
    :return:
    """
    db_type = request.POST.get("type")
    ip = request.POST.get("ip")
    port = request.POST.get("port")
    username = request.POST.get("username")
    password = request.POST.get("password")
    db = request.POST.get("db")
    db = DB(username, password, ip, db, port)
    flag = False
    if db_type == "Oracle":
        if db.connection_oracle():
            flag = True
    elif db_type == "Mysql":
        if db.connection_mysql():
            flag = True
    elif db_type == "Sqlserver":
        if db.connection_sqlserver():
            flag = True
    db.close()
    if flag:
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "连接成功"})
    else:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": db.err})


def DatabaseList(request):
    """
    获取数据库列表 有name的时候为单一查询，用于修改
    :param request:
    :return:
    """
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    name = request.GET.get("name")
    if name:
        db_list = sqlite3_db.get_json("select NAME, type, DB, IP, PORT, USERNAME, STATUS"
                                      " from T_API_DATABASES WHERE NAME='%s'" % name)
    else:
        db_list = sqlite3_db.get_json("select NAME, type, DB, IP||':'||PORT as IP_PORT, USERNAME, CREATE_TIME, STATUS"
                                      " from T_API_DATABASES")
    if db_list:
        db_list = json.loads(db_list)
    else:
        db_list = []
    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "查询成功", "DATA": db_list})


@require_http_methods(["POST"])
def ChangeStatus(request):
    """
    更改数据库使用激活状态
    :param request:
    :return:
    """
    optype = request.POST.get("type")
    status = request.POST.get("status")
    name = request.POST.get("name")
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    sql = ""
    if optype == "database_qyzt":
        sql = "update T_API_DATABASES set status='%s' where name='%s'" % (status, name)
    elif optype == "api_qyzt":
        sql = "update T_API_CONFIG set status='%s' where name='%s'" % (status, name)
    elif optype == "return_field":
        sql = "update T_API_CONFIG set return_field='%s' where name='%s'" % (status, name)
    elif optype == "return_target_table_or_view":
        sql = "update T_API_CONFIG set return_target_table_or_view='%s' where name='%s'" % (status, name)
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": 1, "RTN_MSG": "修改状态成功"})
    if sqlite3_db.execute(sql):
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})


def DatabaseManagement(request):
    """
    数据库管理首页 数据库新增，修改接口
    :param request:
    :return:
    """
    if request.method == "POST":
        name = request.POST.get("name")
        if not name:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "名称不可为空"})
        db_type = request.POST.get("type")
        ip = request.POST.get("ip")
        port = request.POST.get("port")
        username = request.POST.get("username")
        password = request.POST.get("password")
        password = Aes(32, SECRET_KEY).encrypt(password)
        db = request.POST.get("db")
        optype = request.POST.get("optype")
        status = request.POST.get("status")
        sqlite3_db = DB(db_path)
        sqlite3_db.connection_sqlite3()
        if optype == "add":
            sql = "insert into T_API_DATABASES(NAME, TYPE, DB, IP, PORT, USERNAME, PASSWORD, CREATE_TIME, STATUS)" \
                  "values('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" \
                  % (
                  name, db_type, db, ip, port, username, password, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                  status)
            msg = "新增成功"
        else:
            sql = "update T_API_DATABASES set TYPE='%s', DB='%s', IP='%s', PORT='%s', USERNAME='%s', PASSWORD='%s', STATUS='%s'," \
                  " CZLX='U', CZSJ='%s' where NAME='%s'" % (db_type, db, ip, port, username, password, status,
                                                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), name)
            msg = "修改成功"
        if sqlite3_db.execute(sql):
            return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg})
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": sqlite3_db.err})
    page = "DatabaseManagement.html"
    database = 1
    return render(request, "base.html", locals())


def sort_for_sql(sort_json):
    """
    将JSON的排序转换成SQL排序
    :param sort_json:
    :return:
    """
    if not sort_json:
        return ""
    sort_str = " order by "
    for k, v in sort_json.items():
        sort_str += k + " " + v + ","
    return sort_str[:-1]


def condition_construct_for_sql(parameters, condition, alias_field):
    """
    将入参根据条件和字段别名转行为sql的条件
    :param parameters:
    :param condition:
    :param alias_field:
    :return:
    """
    if not alias_field:
        alias_field = {}
    condition_str = ""
    condition_dict = {"GT": " %s > %s ", "GT-NUMBER": " %s > %s ", "LT": "%s < %s", "LT-NUMBER": "%s < %s",
                      "LE": "%s <= %s ", "LE-NUMBER": "%s <= %s ", "GE": " %s >= %s ", "GE-NUMBER": " %s >= %s ",
                      "EQ-NUMBER": " %s = %s", "EQ-CHAR": " %s = '%s'", "BETWEEN": "%s > %s and %s < %s",
                      "EQ": " %s = '%s'", "LIKE": "(%s like '%%%s' or %s like '%s%%')", "NE": " %s != '%s'",
                      "NE-NUMBER": " %s != %s",
                      "NOT LIKE": "(%s not like '%%%s' and %s not like '%s%%')", "IN": "%s in (%s)", "NOT IN": "%s not in (%s)"}  # 条件转义字典 默认比较是数字 等于是字符
    for k in parameters.keys():     # 遍历入参数
        data_type = ""  # 数据类型
        if parameters[k]:       # 没有值则不进行条件拼接
            if "TYPE" in condition[k.upper()].keys():
                data_type = '-' + condition[k.upper()]["type"]
            if k.upper() in alias_field.keys():
                if condition[alias_field[k.upper()]]["OP" + data_type] == "BETWEEN":
                    parameters = parameters.replace('\'', '\\')     # 转义单引号
                    value = parameters[k].split(',')        # 逗号分割两个参数
                    condition_str += condition_dict[condition[k.upper()]["OP"]] % (k.upper(), value[0], k.upper(), value[1]) + " and "
                elif condition[alias_field[k.upper()]]["OP" + data_type] == "LIKE" or condition[alias_field[k.upper()]]["OP" + data_type] == "NOT LIKE":
                    value = parameters[k]
                    condition_str += condition_dict[condition[alias_field[k.upper()]]["OP"]] % (
                    alias_field[k.upper()], value, alias_field[k.upper()], value) + " and "
                elif condition[alias_field[k.upper()]]["OP" + data_type] == "IN" or condition[alias_field[k.upper()]]["OP" + data_type] == "NOT IN":
                    value = parameters[k]
                    condition_str += condition_dict[condition[alias_field[k.upper()]]["OP" + data_type]] % (
                    alias_field[k.upper()], value) + " and "
                else:
                    condition_str += condition_dict[condition[k.upper()]["OP" + data_type]] % (alias_field[k.upper()], parameters[k].replace('\'', '\\')) + " and "
            elif k.upper() in condition.keys():   # 转大写 判断入参key是否在条件里面 或者在 别名字段里面
                if condition[k.upper()]["OP" + data_type] == "BETWEEN":
                    parameters = parameters.replace('\'', '\\')     # 转义单引号
                    value = parameters[k].split(',')        # 逗号分割两个参数
                    condition_str += condition_dict[condition[k.upper()]["OP"]] % (k.upper(), value[0], k.upper(), value[1]) + " and "
                elif condition[k.upper()]["OP" + data_type] == "LIKE" or condition[k.upper()]["OP" + data_type] == "NOT LIKE":
                    value = parameters[k]
                    condition_str += condition_dict[condition[k.upper()]["OP"]] % (
                    k.upper(), value, k.upper(), value) + " and "
                elif condition[k.upper()]["OP" + data_type] == "IN" or condition[k.upper()]["OP" + data_type] == "NOT IN":
                    value = parameters[k]
                    condition_str += condition_dict[condition[k.upper()]["OP"]] % (
                    k.upper(), value) + " and "
                else:
                    condition_str += condition_dict[condition[k.upper()]["OP" + data_type]] % (k.upper(), parameters[k].replace('\'', '\\')) + " and "
    condition_str = condition_str[:-4]
    if condition_str:
        condition_str = "where " + condition_str
    return condition_str


def parameters_vail(parameters, rules, alias_field):
    """
    参数校验
    :param parameters:
    :param rules:
    :param alias_field:
    :return:
    """
    if not rules:
        rules = {}
    for k in parameters.keys():
        if k.upper() not in rules.keys():           # 不在表字段
            if k.upper() not in alias_field.keys():     # 不在别名定义
                return False
            elif k.upper() in alias_field.keys() and alias_field[k.upper()] not in rules.keys():    # 在别名里面 但是不在规则里面
                return False
        elif rules[k.upper()] != "":                # 规则判断
            if "RE" in rules[k.upper()].keys():     # 自定义正则
                if not re.match(rules[k.upper()]['RE'], parameters[k]):     # 正则校验参数合法性
                    return False
            else:
                if "TYPE" in rules[k.upper()].keys():   # 自定义数据类型 否则不检查
                    if rules[k]["TYPE"] == "NUMBER":
                        re.match(r'\d*', parameters[k])  # 正则校验参数合法性
                    else:
                        return False
    return True


def insert_sql_construct(parameters,  alias_fields, table):
    """
    插入SQL构造
    :param parameters:
    :param alias_fields:
    :param table:
    :return:
    """
    sql = "insert into %s " % table
    fields = ""
    values = ""
    if not alias_fields:
        alias_fields = {}
    for k in parameters.keys():
        values += '\'' + parameters[k] + '\','       # 值
        if k.upper() in alias_fields.keys():
            k = alias_fields[k.upper()]
        fields += k + ','                   # 健
    return sql + '(' + fields[:-1] + ') ' + "values(" + values[:-1] + ')'


def delete_sql_construct(parameters, alias_fields, table):
    """
    构造删除sql
    :param parameters:
    :param alias_fields:
    :param table:
    :return:
    """
    sql = "delete from %s where " % table
    conditions = ""
    for k in parameters.keys():
        if isinstance(parameters[k], int):
            values = parameters[k]       # 值
        else:
            values = '\'' + parameters[k] + '\''       # 值
        if k.upper() in alias_fields.keys():
            k = alias_fields[k.upper()]
        if isinstance(parameters[k], int):
            conditions += k + '=' + str(values) + " and "                  # 健
        else:
            conditions += k + '=' + values + " and "                  # 健
    return sql + conditions[:-4]


def update_sql_construct(parameters, update_fields, condition_fields, alias_fields, table):
    """
    构造更新sql
    :param condition_fields:
    :param update_fields:
    :param parameters:
    :param alias_fields:
    :param table:
    :return:
    """
    sql = "update %s set " % table
    kv = ""
    conditions = " where "
    v = ""
    for k in parameters.keys():     # 构造更新参数
        if isinstance(parameters[k], str):
            v = '\'' + parameters[k] + '\''
        elif isinstance(parameters[k], int):
            v = parameters[k]
        if k.upper() in update_fields.keys():
            kv += k.upper() + '=' + v + ","  # 健
        elif k.upper() not in condition_fields.keys() and k.upper() in alias_fields.keys():         # 在别名里面 但是别名不在条件字段里面
            if alias_fields[k.upper()] in update_fields.keys():
                k = alias_fields[k.upper()]
                kv += k.upper() + '=' + v + ","  # 健

    for k in parameters.keys():     # 构造条件参数
        if isinstance(parameters[k], str):
            v = '\'' + parameters[k] + '\''  # 值
        elif isinstance(parameters[k], int):
            v = parameters[k]
        if k.upper() in alias_fields.keys():         # 在别名里面
            if alias_fields[k.upper()] in condition_fields.keys() or k.upper() in condition_fields.keys():      #
                k = alias_fields[k.upper()]
                conditions += k + '=' + v + " and "     # 健
        else:
            if k.upper() in condition_fields.keys():
                if isinstance(v, int):
                    conditions += k + '=' + str(v) + " and "  # 健
                else:
                    conditions += k + '=' + v + " and "  # 健
    return sql + kv[:-1] + conditions[:-4]


def login_require(func):
    @wraps(func)
    def check(*args, **kwargs):
        no_auth_path = {'dcrecorder': {"INSERT": True, "UPDATE": False}}
        req = args[0]
        path = args[1].split('/')
        if path[0].lower() in no_auth_path.keys():
            if len(path) == 1:
                return func(*args, **kwargs)
            if path[1].upper() in no_auth_path[path[0]].keys():
                if len(path) > 1 and no_auth_path[path[0]][path[1].upper()]:
                    return func(*args, **kwargs)
        session_id = req.COOKIES.get("_sessionid", None)
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        if not session_id or not r.hget(session_id, "login_time"):
            return redirect(reverse("login"))
        r.expire(session_id, 3600)
        return func(*args, **kwargs)
    return check


@csrf_exempt
@PrivilegesWrapper(check_type="api", log2db=True)
def index(request, path):
    """
    使用sqlite3数据库
    接口访问控制：IP限制， token限制，方法限制, 入参控制
    分页：page：页码， 放在GET里
    :param request:
    :param path:
    :return:
    """
    path = path.split('/')
    op = ''
    if len(path) == 1:
        path = path[0]
    else:
        op = path[1]
        path = path[0]
    method = request.method                 # 调用方式
    ip = request.META["REMOTE_ADDR"]        # 访问IP
    page = request.GET.get("page", None)  # 页码分页
    offset = request.GET.get("offset", None)  # 偏移分页
    limit = request.GET.get("limit", None)  # 限制返回条数
    parameters = dict(zip(request.GET.keys(), request.GET.values()))  # 携带数据
    if not parameters:
        content_type = request.META.get("CONTENT_TYPE")
        if request.body:
            if re.search(r'json', content_type, re.I):
                parameters = json.loads(str(request.body, encoding='utf-8'))
            else:
                k = [urllib.parse.unquote_plus(x.split('=')[0]) for x in str(request.body, encoding="utf-8").split('&')]
                v = [urllib.parse.unquote_plus(x.split('=')[1]) for x in str(request.body, encoding="utf-8").split('&')]
                parameters = dict(zip(k, v))
    except_key = ["csrfmiddlewaretoken", "offset", "page", "limit"]
    for var in except_key:
        if var in parameters.keys():
            parameters.pop(var)
    # 获取接口组装参数
    sql = "select a.URL, a.ALLOW_METHOD, a.ALLOW_IP,a.TARGET_TABLE_OR_VIEW, a.EXECUTE_SQL, a.PER_PAGE, " \
          "a.RETURN_TARGET_TABLE_OR_VIEW, a.STATUS API_STATUS, a.RETURN_FIELD, a.SORT, a.CONDITION, a.ALIAS_FIELDS," \
          "a.INSERT_STATUS, a.DELETE_STATUS, a.UPDATE_STATUS, a.INSERT_FIELDS, a.DELETE_FIELDS, a.UPDATE_FIELDS," \
          "a.RETURN_FIELDS,a.RETURN_TOTAL, b.TYPE, b.DB, b.IP," \
          "b.PORT, b.USERNAME, b.PASSWORD, b.STATUS DB_STATUS from T_API_CONFIG a, T_API_DATABASES b where a.STATUS='1'" \
          " and b.STATUS='1' and a.TARGET_DB=b.NAME and a.url='%s'" % path
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    data = sqlite3_db.get_json(sql)
    if data:
        data = json.loads(data.replace("\\\\", "\\"))[0]
    else:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口未启用或不存在"}, json_dumps_params={'ensure_ascii': False})  # 截断
    # 数据库连接数据
    db_type = data['TYPE']
    host = data['IP']
    port = data['PORT']
    username = data['USERNAME']
    password = data['PASSWORD']
    db = data['DB']
    # 接口配置数据
    allow_method = data['ALLOW_METHOD']
    allow_ip = data['ALLOW_IP']
    target_table_or_view = data['TARGET_TABLE_OR_VIEW']
    execute_sql = data['EXECUTE_SQL'].replace("&quto", "'")
    return_target_table_or_view = data['RETURN_TARGET_TABLE_OR_VIEW']
    return_field = data['RETURN_FIELD']     # 是否返回字段
    return_fields = data['RETURN_FIELDS']   # 返回字段列表
    return_total = data['RETURN_TOTAL']   # 返回记录数量
    per_page = data['PER_PAGE']
    RESTFUL = False
    # CRUD操作规则判断
    insert_fields = data['INSERT_FIELDS']
    if insert_fields:
        insert_fields = json.loads(insert_fields)
    delete_fields = data['DELETE_FIELDS']
    if delete_fields:
        delete_fields = json.loads(delete_fields)
    update_fields = data['UPDATE_FIELDS']
    if update_fields:
        update_fields = json.loads(update_fields)
    if op and op.upper() not in ["INSERT", "UPDATE", "DELETE"]:
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "404 No Found"}, status=404)  # 截止
    if op:
        if op.upper() == "INSERT":  # 检测操作合理性
            if data['INSERT_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持新增操作"}, json_dumps_params={'ensure_ascii': False})  # 截止
        elif op.upper() == "DELETE":
            if data['DELETE_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持删除操作"}, json_dumps_params={'ensure_ascii': False})  # 截止
        elif op.upper() == "UPDATE":
            if data['UPDATE_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持修改操作"}, json_dumps_params={'ensure_ascii': False})  # 截止
    elif RESTFUL:
        if request.method == "POST":  # 检测操作合理性
            if data['INSERT_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持新增操作"},
                                    json_dumps_params={'ensure_ascii': False})  # 截止
        elif request.method == "DELETE":
            if data['DELETE_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持删除操作"},
                                    json_dumps_params={'ensure_ascii': False})  # 截止
        elif request.method == "PUT" or request.method == "PATCH":
            if data['UPDATE_STATUS'] == '0':
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持修改操作"},
                                    json_dumps_params={'ensure_ascii': False})  # 截止
    alias_fields = data['ALIAS_FIELDS']                         # 排序
    if alias_fields:
        alias_fields = json.loads(alias_fields)
    else:
        alias_fields = {}
    condition = data['CONDITION']                               # 条件
    if condition and not op:        # 查询才对条件进行检查
        condition = json.loads(condition)
        # 入参控制
        for k in parameters.keys():
            if k.upper() != 'PAGE' and k.upper() not in condition.keys() and k.upper() not in alias_fields.keys():
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "非法条件：%s" % k},
                                    json_dumps_params={'ensure_ascii': False})  # 截止
    sort = data['SORT']                                         # 排序
    if sort:
        sort = json.loads(sort)
    res_data = {}
    # ip控制
    if allow_ip != '*':
        if ip not in allow_ip.split(','):                         # 全部IP放行
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "IP限制, 禁止访问"}, json_dumps_params={'ensure_ascii': False})  # 截止

    # 方法控制
    if allow_method != 'ALL' and allow_method != method:                   # 全部方法放行
        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "方法限制, 禁止访问"}, json_dumps_params={'ensure_ascii': False})  # 截止
    # 数据库连接
    connect_db = DB(username, Aes.decrypt(password, SECRET_KEY), host, db, port)
    # Mysql库支持
    sql = ""
    msg = ""
    if db_type == "Mysql":
        if connect_db.connection_mysql():
            if op:  # 操作判定
                # 入参合法性验证
                if op.upper() == "INSERT":      # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = "select c.COLUMN_NAME ,c.COLUMN_TYPE ,c.COLUMN_COMMENT from\
                            information_schema.COLUMNS c ,information_schema.TABLES t where c.TABLE_NAME = t.TABLE_NAME\
                            and t.TABLE_SCHEMA = '%s' and t.TABLE_NAME='%s'" % (db, target_table_or_view)
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if op.upper() == "DELETE":      # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if op.upper() == "UPDATE":
                    if not update_fields:       # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():       # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]), alias_fields):      # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":        # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            elif RESTFUL and request.method != 'GET':
                if request.method == "POST":      # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = "select c.COLUMN_NAME ,c.COLUMN_TYPE ,c.COLUMN_COMMENT from\
                            information_schema.COLUMNS c ,information_schema.TABLES t where c.TABLE_NAME = t.TABLE_NAME\
                            and t.TABLE_SCHEMA = '%s' and t.TABLE_NAME='%s'" % (db, target_table_or_view)
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if request.method == "DELETE":      # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if request.method == "PUT" or request.method == "PATCH":
                    if not update_fields:       # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():       # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]), alias_fields):      # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":        # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            # 查询模块
            return_fields_str = " "
            if return_fields:
                for var in json.loads(return_fields):
                    return_fields_str += var + ","
                return_fields_str = return_fields_str[:-1] + " "
            else:
                return_fields_str = " * "
            if execute_sql:                 # 返回自定义sql数据
                if condition:
                    execute_sql = "select * from (" + execute_sql + ") t " + condition_construct_for_sql(parameters, condition, alias_fields)
                if per_page != "ALL":
                    if page:  # 有分页信息就分页显示 没有则返回第一页
                        if limit:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %s OFFSET %s " % (
                                sort_for_sql(sort), limit, (int(page) - 1) * int(limit))
                        else:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %s OFFSET %s " % (
                            sort_for_sql(sort), per_page, (int(page) - 1) * int(per_page))
                    elif offset:
                        if limit:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %s OFFSET %s " % (
                            sort_for_sql(sort), limit, offset)
                        else:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %s OFFSET %s " % (
                            sort_for_sql(sort), per_page, offset)
                    else:
                        sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %s OFFSET 0 " % (
                            sort_for_sql(sort), per_page)  # 第一页
                    data = connect_db.get_json(sql)
                else:
                    data = connect_db.get_json(execute_sql)
                if not data:        # 返回None
                    data = '[]'
                res_data["DATA"] = json.loads(data.replace('\\"', '\"'))
                if connect_db.err:
                    res_data["ERROR_MSG"] = connect_db.err
            elif return_target_table_or_view == '1':                        # 返回表数据
                if condition:
                    sql = "select %s from %s %s %s" % (return_fields_str, target_table_or_view, condition_construct_for_sql(parameters, condition, alias_fields), sort_for_sql(sort))    # 字段控制
                else:
                    sql = "select %s from %s %s" % (return_fields_str, target_table_or_view, sort_for_sql(sort))
                if per_page != "ALL":
                    if page:
                        if limit:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %s OFFSET %s " % (sort_for_sql(sort), limit, (int(page) - 1) * int(limit))
                        else:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %s OFFSET %s " % (sort_for_sql(sort), per_page, (int(page) - 1) * int(per_page))
                    elif offset:
                        if limit:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %s OFFSET %s " % (sort_for_sql(sort), limit, offset)
                        else:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %s OFFSET %s " % (sort_for_sql(sort), per_page, offset)
                    else:
                        sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %s OFFSET 0 " % (sort_for_sql(sort), per_page)
                data = connect_db.get_json(sql) # 返回目标表
                if data:
                    # data = json.loads(data.replace(': "{', ': {').replace('}"}', '}}'))
                    data = json.loads(data.replace('\\"', '\"'))
                    res_data["DATA"] = data
                else:
                    res_data["DATA"] = []
                if connect_db.err:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err}, json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "接口没有数据"}, json_dumps_params={'ensure_ascii': False})
            if return_field == '1':  # 返回字段信息控制
                sql = "select c.COLUMN_NAME ,c.COLUMN_TYPE ,c.COLUMN_COMMENT from " \
                      "information_schema.COLUMNS c ,information_schema.TABLES t where c.TABLE_NAME = t.TABLE_NAME" \
                      " and t.TABLE_SCHEMA = '%s' and t.TABLE_NAME='%s'" % (db, target_table_or_view)
                filed_comment = connect_db.get_json(sql)  # 字段数据
                if filed_comment:
                    filed_comment = json.loads(filed_comment)
                    res_data["FIELDS"] = filed_comment
                else:
                    res_data["FIELDS"] = []
            if return_total == '1':
                if execute_sql:
                    sql = "select count(*) TOTAL from (%s) tmp_count %s" % (execute_sql, condition_construct_for_sql(parameters, condition, alias_fields))
                else:
                    sql = "select count(*) TOTAL from %s %s" % (target_table_or_view, condition_construct_for_sql(parameters, condition, alias_fields))
                total = json.loads(connect_db.get_json(sql))[0]["TOTAL"]  # 返回总数
                res_data["TOTAL"] = total if total else 0
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库%s连接失败, %s" % (db, connect_db.err)},
                                json_dumps_params={'ensure_ascii': False})
    # Oralce库支持
    elif db_type == "Oracle":
        if connect_db.connection_oracle():
            if op:  # 操作判定
                # 入参合法性验证
                if op.upper() == "INSERT":  # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = "select COLUMN_NAME, DATA_TYPE from user_tab_columns where Table_Name='%s' order by column_name" % target_table_or_view
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if op.upper() == "DELETE":  # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if op.upper() == "UPDATE":
                    if not update_fields:  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters,
                                           dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]),
                                           alias_fields):  # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":  # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            elif RESTFUL:
                # 入参合法性验证
                if request.method == "POST":  # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = "select COLUMN_NAME, DATA_TYPE from user_tab_columns where Table_Name='%s' order by column_name" % target_table_or_view
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if request.method == "DELETE":  # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if request.method == "PUT" or request.meta == "PATCH":
                    if not update_fields:  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters,
                                           dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]),
                                           alias_fields):  # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":  # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})

            # 查询模块
            return_fields_str = " "
            if return_fields:
                for var in json.loads(return_fields):
                    return_fields_str += var + ","
                return_fields_str = return_fields_str[:-1] + " "
            else:
                return_fields_str = " * "
            if execute_sql:  # 返回自定义sql数据
                if condition:
                    execute_sql = "select t_num.*, ROWNUM rn from(select * from (" + execute_sql + ") t) t_num" + condition_construct_for_sql(parameters,
                                                                                                         condition,
                                                                                                         alias_fields)
                if per_page != "ALL":
                    if page:  # 有分页信息就分页显示 没有则返回第一页
                        if limit:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + execute_sql + ") t %s ) t_tmp where rn BETWEEN %s and %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(limit) + 1, (int(page) - 1) * int(limit) + int(limit))
                        else:
                            sql = "select t_tmp.*  from (select %s from (" % return_fields_str + execute_sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(per_page) + 1, (int(page) - 1) * int(per_page) + int(per_page))
                    elif offset:
                        if limit:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + execute_sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                                sort_for_sql(sort), int(offset) + 1, int(offset) + int(limit))
                        else:
                            sql = "select t_tmp.*  from (select %s from (" % return_fields_str + execute_sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                                sort_for_sql(sort), int(offset) + 1, int(per_page) + int(offset))
                    else:
                        sql = "select t_tmp.*  (select %s from (" % return_fields_str + execute_sql + ") t %s) t_tmp where rn BETWEEN 0 and %s " % (
                            sort_for_sql(sort), per_page)  # 第一页
                    data = connect_db.get_json(sql)
                else:
                    data = connect_db.get_json(execute_sql)
                if not data:  # 返回None
                    data = '[]'
                res_data["DATA"] = json.loads(data)
                if connect_db.err:
                    res_data["ERROR_MSG"] = connect_db.err
            elif return_target_table_or_view == '1':  # 返回表数据
                if condition:
                    sql = "select t_num.*, ROWNUM rn from( select %s from %s %s %s ) t_num" % (return_fields_str, target_table_or_view,
                                                       condition_construct_for_sql(parameters, condition, alias_fields),
                                                       sort_for_sql(sort))  # 字段控制
                else:
                    sql = "select t_num.*, ROWNUM rn from(select %s, ROWNUM rn from %s %s ) t_num" % (return_fields_str, target_table_or_view, sort_for_sql(sort))
                if per_page != "ALL":
                    if page:
                        if limit:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                            sort_for_sql(sort), (int(page) - 1) * int(limit) + 1, (int(page) - 1) * int(limit) + int(limit))
                        else:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                            sort_for_sql(sort), (int(page) - 1) * int(per_page) + 1, (int(page) - 1) * int(per_page) + int(per_page) )
                    elif offset:
                        if limit:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                            sort_for_sql(sort), int(offset) + 1, int(offset) + int(limit))
                        else:
                            sql = "select t_tmp.* from (select %s from (" % return_fields_str + sql + ") t %s) t_tmp where rn BETWEEN %s and %s " % (
                            sort_for_sql(sort), int(offset) + 1, int(per_page) + int(offset))
                    else:
                        sql = "select t_tmp.* from (select %s from (" % return_fields_str + sql + ") t %s) t_tmp where rn BETWEEN 0 and %s " % (
                        sort_for_sql(sort), per_page)
                data = connect_db.get_json(sql)  # 返回目标表
                if data:
                    data = json.loads(data)
                    res_data["DATA"] = data
                else:
                    res_data["DATA"] = []
                if connect_db.err:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "接口没有数据"}, json_dumps_params={'ensure_ascii': False})
            if return_field == '1':  # 返回字段信息控制
                sql = "select t1.COLUMN_NAME, t1.DATA_TYPE, t2.COMMENTS from user_tab_columns t1 LEFT JOIN " \
                      "user_col_comments t2 on t1.COLUMN_name=t2.COLUMN_NAME and t1.Table_Name=t2.Table_Name where " \
                      "t1.table_name='%s' order by t1.column_name" % target_table_or_view       # oracle获取字段名 类型 备注
                filed_comment = connect_db.get_json(sql)  # 字段数据
                if filed_comment:
                    filed_comment = json.loads(filed_comment)
                    res_data["FIELDS"] = filed_comment
                else:
                    res_data["FIELDS"] = []
            if return_total == '1':
                sql = "select count(*) TOTAL from %s %s" % (
                target_table_or_view, condition_construct_for_sql(parameters, condition, alias_fields))
                total = json.loads(connect_db.get_json(sql))[0]["TOTAL"]  # 返回总数
                res_data["TOTAL"] = total
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库%s连接失败, %s" % (db, connect_db.err)},
                                json_dumps_params={'ensure_ascii': False})
    elif db_type == "Sqlserver":
        if connect_db.connection_sqlserver():
            if op:  # 操作判定
                # 入参合法性验证
                if op.upper() == "INSERT":  # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = '''
                        SELECT [COLUMN_NAME] = [Columns].name ,
                                [COLUMN_COMMENT] = [Properties].value,
                                [COLUMN_TYPE] = [Types].name
                        FROM    sys.tables AS [Tables]
                                INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                                INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                                   AND is_user_defined = 0
                                                                   AND [Types].name <> 'sysname'
                                LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                                      AND [Properties].minor_id = [Columns].column_id
                                                                                      AND [Properties].name = 'MS_Description'
                        WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
                        ORDER BY [Columns].column_id''' % target_table_or_view
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if op.upper() == "DELETE":  # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if op.upper() == "UPDATE":
                    if not update_fields:  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters,
                                           dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]),
                                           alias_fields):  # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":  # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            elif RESTFUL:
                if request.method == "POST":  # 插入SQL拼接
                    if not insert_fields:  # 没有定义插入字段 则全部字段都可以插入
                        insert_fields = {}
                        sql = '''
                        SELECT [COLUMN_NAME] = [Columns].name ,
                                [COLUMN_COMMENT] = [Properties].value,
                                [COLUMN_TYPE] = [Types].name
                        FROM    sys.tables AS [Tables]
                                INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                                INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                                   AND is_user_defined = 0
                                                                   AND [Types].name <> 'sysname'
                                LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                                      AND [Properties].minor_id = [Columns].column_id
                                                                                      AND [Properties].name = 'MS_Description'
                        WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
                        ORDER BY [Columns].column_id''' % target_table_or_view
                        res = json.loads(connect_db.get_json(sql))
                        for var in res:
                            insert_fields[var["COLUMN_NAME"]] = ""
                    if not parameters_vail(parameters, insert_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "新增操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = insert_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "新增成功"
                if request.method == "DELETE":  # 删除SQL拼接
                    if not delete_fields:
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何条件的删除"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters, delete_fields, alias_fields):  # 参数校验
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "删除操作含有非法字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = delete_sql_construct(parameters, alias_fields, target_table_or_view)
                    msg = "删除成功"
                if request.method == "PUT" or request.method == "PATCH":
                    if not update_fields:  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "该接口不支持任何字段的修改"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "UPDATE_FIELDS" not in update_fields.keys():  # 没有定义编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "可编辑字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if "CONDITION_FIELDS" not in update_fields.keys():
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "条件字段未定义"},
                                            json_dumps_params={'ensure_ascii': False})
                    if not parameters_vail(parameters,
                                           dict(update_fields["UPDATE_FIELDS"], **update_fields["CONDITION_FIELDS"]),
                                           alias_fields):  # 校验可编辑字段
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "含有非法编辑字段"},
                                            json_dumps_params={'ensure_ascii': False})
                    sql = update_sql_construct(parameters, update_fields["UPDATE_FIELDS"],
                                               update_fields["CONDITION_FIELDS"], alias_fields, target_table_or_view)
                    if sql[-2:] == "wh":  # 条件被截断错误
                        return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "更新操作配置错误"},
                                            json_dumps_params={'ensure_ascii': False})
                    msg = "更新成功"
                # 执行数据库增删改操作
                if connect_db.execute(sql):
                    return JsonResponse({"RTN_CODE": 1, "RTN_MSG": msg},
                                        json_dumps_params={'ensure_ascii': False})
                else:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            # 查询模块
            return_fields_str = " "
            if return_fields:
                for var in json.loads(return_fields):
                    return_fields_str += var + ","
                return_fields_str = return_fields_str[:-1] + " "
            else:
                return_fields_str = " * "
            if execute_sql:  # 返回自定义sql数据
                sql = '''
                SELECT top 1 [COLUMN_NAME] = [Columns].name ,
                        [COLUMN_COMMENT] = [Properties].value,
                        [COLUMN_TYPE] = [Types].name
                FROM    sys.tables AS [Tables]
                        INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                        INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                           AND is_user_defined = 0
                                                           AND [Types].name <> 'sysname'
                        LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                              AND [Properties].minor_id = [Columns].column_id
                                                                              AND [Properties].name = 'MS_Description'
                WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
                ORDER BY [Columns].column_id''' % target_table_or_view
                res = json.loads(connect_db.get_json(sql))  # 获取列来进行分页
                if condition:
                    execute_sql = "select t_num.*, row_number() over(order by t_num.%s) rn from(" \
                                  "select * from (" % res[0]['COLUMN_NAME'] + execute_sql + ") t) t_num" + condition_construct_for_sql(
                        parameters,
                        condition,
                        alias_fields)
                if per_page != "ALL":
                    if page:  # 有分页信息就分页显示 没有则返回第一页
                        if limit:
                            sql = "select top %s t_tmp.* from (select %s from (" % (limit, return_fields_str) + execute_sql + ") t %s ) t_tmp where rn > %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(limit))
                        else:
                            sql = "select top %s t_tmp.*  from (select %s from (" % (per_page, return_fields_str) + execute_sql + ") t %s) t_tmp where rn > %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(per_page))
                    elif offset:
                        if limit:
                            sql = "select top %s t_tmp.* from (select %s from (" % (limit, return_fields_str) + execute_sql + ") t %s) t_tmp where rn  > %s " % (
                                sort_for_sql(sort), offset)
                        else:
                            sql = "select top %s t_tmp.*  from (select %s from (" % (per_page, return_fields_str) + execute_sql + ") t %s) t_tmp where rn > %s  " % (
                                sort_for_sql(sort), int(offset))
                    else:
                        sql = "select top %s t_tmp.*  (select %s from (" % (per_page, return_fields_str) + execute_sql + ") t %s) t_tmp where rn > 0 " % sort_for_sql(sort)  # 第一页
                    data = connect_db.get_json(sql)
                else:
                    data = connect_db.get_json(execute_sql)
                if not data:  # 返回None
                    data = '[]'
                res_data["DATA"] = json.loads(data)
                if connect_db.err:
                    res_data["ERROR_MSG"] = connect_db.err
            elif return_target_table_or_view == '1':  # 返回表数据
                sql = '''
                SELECT top 1 [COLUMN_NAME] = [Columns].name ,
                        [COLUMN_COMMENT] = [Properties].value,
                        [COLUMN_TYPE] = [Types].name
                FROM    sys.tables AS [Tables]
                        INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                        INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                           AND is_user_defined = 0
                                                           AND [Types].name <> 'sysname'
                        LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                              AND [Properties].minor_id = [Columns].column_id
                                                                              AND [Properties].name = 'MS_Description'
                WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
                ORDER BY [Columns].column_id''' % target_table_or_view
                res = json.loads(connect_db.get_json(sql))  # 获取列来进行分页
                if condition:
                    sql = "select t_num.*, row_number() over(order by t_num.%s) rn from( select %s from %s %s %s ) t_num" % (
                    res[0]["COLUMN_NAME"], return_fields_str, target_table_or_view,
                    condition_construct_for_sql(parameters, condition, alias_fields),
                    sort_for_sql(sort))  # 字段控制
                else:
                    sql = "select t_num.*,row_number() over(order by t_num.%s) rn from(select %s from %s %s ) t_num" % (
                    res[0]["COLUMN_NAME"], return_fields_str, target_table_or_view, sort_for_sql(sort))
                if per_page != "ALL":
                    if page:
                        if limit:
                            sql = "select top %s t_tmp.* from (select %s from (" % (limit, return_fields_str) + sql + ") t %s) t_tmp where rn > %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(limit))
                        else:
                            sql = "select top %s t_tmp.* from (select %s from (" % (per_page, return_fields_str) + sql + ") t %s) t_tmp where rn > %s " % (
                                sort_for_sql(sort), (int(page) - 1) * int(per_page))
                    elif offset:
                        if limit:
                            sql = "select top %s t_tmp.* from (select %s from (" % (limit, return_fields_str) + sql + ") t %s) t_tmp where rn > %s " % (
                                sort_for_sql(sort), int(offset))
                        else:
                            sql = "select top %s t_tmp.* from (select %s from (" % (per_page, return_fields_str) + sql + ") t %s) t_tmp where rn > %s " % (
                                sort_for_sql(sort), int(offset))
                    else:
                        sql = "select top %s t_tmp.* from (select %s from (" % (per_page, return_fields_str) + sql + ") t %s) t_tmp where rn > 0" % sort_for_sql(sort)
                data = connect_db.get_json(sql)  # 返回目标表
                if data:
                    data = json.loads(data)
                    res_data["DATA"] = data
                else:
                    res_data["DATA"] = []
                if connect_db.err:
                    return JsonResponse({"RTN_CODE": 0, "RTN_MSG": connect_db.err},
                                        json_dumps_params={'ensure_ascii': False})
            else:
                return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "接口没有数据"}, json_dumps_params={'ensure_ascii': False})
            if return_field == '1':  # 返回字段信息控制
                sql = '''
                    SELECT top 1 [COLUMN_NAME] = [Columns].name ,
                            [COLUMN_COMMENT] = [Properties].value,
                            [COLUMN_TYPE] = [Types].name
                    FROM    sys.tables AS [Tables]
                            INNER JOIN sys.columns AS [Columns] ON [Tables].object_id = [Columns].object_id
                            INNER JOIN sys.types AS [Types] ON [Columns].system_type_id = [Types].system_type_id
                                                               AND is_user_defined = 0
                                                               AND [Types].name <> 'sysname'
                            LEFT OUTER JOIN sys.extended_properties AS [Properties] ON [Properties].major_id = [Tables].object_id
                                                                                  AND [Properties].minor_id = [Columns].column_id
                                                                                  AND [Properties].name = 'MS_Description'
                    WHERE   [Tables].name ='%s' -- and [Columns].name = '字段名'
                    ORDER BY [Columns].column_id''' % target_table_or_view
                filed_comment = connect_db.get_json(sql)  # 字段数据
                if filed_comment:
                    filed_comment = json.loads(filed_comment)
                    res_data["FIELDS"] = filed_comment
                else:
                    res_data["FIELDS"] = []
            if return_total == '1':
                sql = "select count(*) TOTAL from %s %s" % (
                    target_table_or_view, condition_construct_for_sql(parameters, condition, alias_fields))
                total = json.loads(connect_db.get_json(sql))[0]["TOTAL"]  # 返回总数
                res_data["TOTAL"] = total
        else:
            return JsonResponse({"RTN_CODE": 0, "RTN_MSG": "数据库%s连接失败, %s" % (db, connect_db.err)},
                                json_dumps_params={'ensure_ascii': False})
    res_data["RTN_CODE"] = 1
    res_data["RTN_MSG"] = "查询成功"
    return JsonResponse(res_data, json_dumps_params={'ensure_ascii': False})

