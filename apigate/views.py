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

# new


def quote_generate(quote_num):
    """
    生成预处理字符串
    :param quote_num:
    :return:
    """
    return ','.join(['?' for i in range(quote_num)])


def filed_generate(fields, alias_fields, op_type='I'):
    """
    生成字段器 FIELD1=?, FIELD2=? | FIELD1, FIELD2
    :param op_type:
    :param alias_fields:
    :param fields:
    :return:
    """
    if op_type == 'I':
        return ','.join([field.upper() if field.upper() in alias_fields.keys() else alias_fields[field.upper()] for field in fields])
    elif op_type == 'U':
        return ','.join(['%s=?' % field.upper() if field.upper() in alias_fields.keys() else alias_fields[field.upper()] for field in fields])


def condition_generate(parameters=None, condition=None, alias_field=None):
    """
    条件生成器 WHERE FILED1=? AND FILED2=?, [VALUES1,...]
    :return:
    """
    if alias_field is None:
        alias_field = {}
    if condition is None:
        condition = {}
    if parameters is None:
        parameters = {}
    if not alias_field:
        alias_field = {}
    condition_dict = {"GT": " %s > ? ", "GT-NUMBER": " %s > ? ", "LT": " %s < ? ", "LT-NUMBER": " %s < ? ",
                      "LE": "%s <= ? ", "LE-NUMBER": "%s <= ? ", "GE": " %s >= ? ", "GE-NUMBER": " %s >= ? ",
                      "EQ-NUMBER": " %s = ? ", "EQ-CHAR": " %s = ? ", "BETWEEN": " %s > ? and %s < ? ",
                      "EQ": " %s = ? ", "LIKE": " (%s like CONCAT('%%', ?) or %s like CONCAT(?, '%%') ", "NE": " %s != ? ",
                      "NE-NUMBER": " %s != ? ",
                      "NOT LIKE": " (%s not like '%%?' and %s not like CONCAT(?, '%%')", "IN": "%s in (%s) ",
                      "NOT IN": " %s not in (%s) "}  # 条件转义字典 默认比较是数字 等于是字符
    condition_list = []
    values = []
    for k in parameters.keys():  # 遍历入参数
        data_type = ""  # 数据类型
        if parameters[k]:  # 没有值则不进行条件拼接
            if "TYPE" in condition[k.upper()].keys():       # 获取是否匹配了类型 支持正则定义
                data_type = '-' + condition[k.upper()]["type"]
            if k.upper() in alias_field.keys():     # 别名字段里面
                value = parameters[k]
                k = alias_field[k.upper()]
                condition_key = condition[k]["OP" + data_type]
            else:
                value = parameters[k]
                k = k.upper()
                condition_key = condition[k]["OP" + data_type]
            if condition[k]["OP" + data_type] == "BETWEEN":
                condition_list.append(condition_dict[condition_key] % (k, k))
                values.extend(value.split(','))
            elif condition_key == "LIKE" or condition_key == "NOT LIKE":
                condition_list.append(condition_dict[condition_key] % (k, k))
                values.extend([value, value])
            elif condition_key == "IN" or condition_key == "NOT IN":
                value = parameters[k].split(',')
                condition_list.append(
                    condition_dict[condition_key] % (condition[k], quote_generate(len(value))))   # 生成 FIELD in (?,...)
                values.extend(value)
            else:
                condition_list.append(
                    condition_dict[condition_key] % (condition[k], quote_generate(len(value))))  # 生成 FIELD in (?,...)
                values.append(value)
    if condition_list:
        return ' AND '.join(condition_list), values
    return '', []


def insert_PreSQL_construct(parameters=None, alias_fields=None, table=None):
    """
    插入预处理SQL构造 INSERT INTO TABLE(FIELD1, ...) VALUES(VALUES1,...)
    :param table:
    :param parameters:
    :param alias_fields:
    :return: PreSQL, Values
    """
    if not table:
        print("表不能为空")
        return
    if alias_fields is None:
        alias_fields = []
    if parameters is None:
        parameters = {}
    return "INSERT INTO %s(%s) VALUES (%s)" % (table, filed_generate(parameters.keys(), alias_fields), quote_generate(len(parameters.values()))), parameters.values()


def delete_PreSQL_construct(parameters=None, alias_fields=None, table=None):
    """
    构造删除预处理函数 DELETE FROM TABLE where FIELD1=? AND ...., [VALUE1,...]
    :param parameters:
    :param alias_fields:
    :param table:
    :return:
    """
    if alias_fields is None:
        alias_fields = []
    if parameters is None:
        parameters = {}
    condition_list = []
    values = []
    for k in parameters.keys():
        value = parameters[k]
        if k.upper() in alias_fields.keys():
            k = alias_fields[k.upper()]
        if isinstance(value, int):
            condition_list.append("%s = ?" % k)
            values.append(value)                     # 值
        else:
            values.append('\'' + value + '\'')       # 值
    return "DELETE FROM %s WHERE %s " % (table, filed_generate(parameters.keys(), alias_fields, op_type='U')), values


def update_PreSQL_construct(parameters, update_fields, condition_fields, alias_fields, table):
    """
    更新预处理语句构造器 UPDATE TABLE SET FIELD1=?, FIELD2=?... WHERE FIELD3=?,...
    :param parameters:
    :param update_fields:
    :param condition_fields:
    :param alias_fields:
    :param table:
    :return:
    """
    condition_list = []
    field_list = []
    condition_values = []
    update_values = []
    for k in parameters.keys():  # 构造更新参数
        value = parameters[k]
        if k.upper() in alias_fields.keys():
            k = alias_fields[k.upper()]
        else:
            k = k.upper()
        if k in update_fields.keys():       # 更新域
            field_list.append(k)
            update_values.append(value)
        else:
            condition_list.append(k)
            condition_values.append(value)
    return "UPDATE %s %s WHERE %s" % (table, filed_generate(field_list, [], op_type='U'),
                                      condition_generate(condition_fields, [])), update_values + condition_values


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


def request_data(request):
    """
    将请求的参数转换成字典
    :param request:
    :return:
    """
    parameters = dict(zip(request.GET.keys(), request.GET.values()))  # GET数据
    if not parameters:
        content_type = request.META.get("CONTENT_TYPE")
        if request.body:
            if re.search(r'json', content_type, re.I):
                parameters = json.loads(str(request.body, encoding='utf-8'))
            else:
                k = [urllib.parse.unquote_plus(x.split('=')[0]) for x in str(request.body, encoding="utf-8").split('&')]
                v = [urllib.parse.unquote_plus(x.split('=')[1]) for x in str(request.body, encoding="utf-8").split('&')]
                parameters = dict(zip(k, v))
            return parameters       # POST
    return parameters               # GET


def except_keys(post_parameters, keys):
    """
    排除用户参数
    :return:
    """
    for var in keys:
        if var in post_parameters.keys():
            post_parameters.pop(var)
    return post_parameters


def get_api_config(api_path):
    """
    获取对应路径的api配置参数
    :param api_path:
    :return:
    """
    # 获取接口组装参数
    sql = "select a.URL, a.ALLOW_METHOD, a.ALLOW_IP,a.TARGET_TABLE_OR_VIEW, a.EXECUTE_SQL, a.PER_PAGE, " \
          "a.RETURN_TARGET_TABLE_OR_VIEW, a.STATUS API_STATUS, a.RETURN_FIELD, a.SORT, a.CONDITION, a.ALIAS_FIELDS," \
          "a.INSERT_STATUS, a.DELETE_STATUS, a.UPDATE_STATUS, a.INSERT_FIELDS, a.DELETE_FIELDS, a.UPDATE_FIELDS," \
          "a.RETURN_FIELDS,a.RETURN_TOTAL, b.TYPE, b.DB, b.IP," \
          "b.PORT, b.USERNAME, b.PASSWORD, b.STATUS DB_STATUS from T_API_CONFIG a, T_API_DATABASES b where a.STATUS='1'" \
          " and b.STATUS='1' and a.TARGET_DB=b.NAME and a.url='%s'" % api_path
    sqlite3_db = DB(db_path)
    sqlite3_db.connection_sqlite3()
    data = sqlite3_db.get_json(sql)
    if data:
        return json.loads(data.replace("\\\\", "\\"))[0]
    return False


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
    alias_fields = data['ALIAS_FIELDS']                         # 别名
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
                            and t.TABLE_SCHEMA = %s and t.TABLE_NAME=%s"
                        res = json.loads(connect_db.get_json(sql, [db, target_table_or_view]))
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
            data = ""
            return_fields_str = " "
            if return_fields:
                for var in json.loads(return_fields):
                    return_fields_str += var + ","
                return_fields_str = return_fields_str[:-1] + " "
            else:
                return_fields_str = " * "
            if execute_sql:                 # 返回自定义sql数据
                if condition:
                    # select * from table where FIELD1=? and FIELD2=?
                    execute_sql = "select * from (" + execute_sql + ") t " + condition_construct_for_sql(parameters, condition, alias_fields)
                limit_offset = []
                if per_page != "ALL":
                    if page:  # 有分页信息就分页显示 没有则返回第一页
                        if limit:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [limit, (int(page) - 1) * int(limit)]
                        else:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [per_page, (int(page) - 1) * int(per_page)]
                    elif offset:
                        if limit:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [limit, offset]
                        else:
                            sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [per_page, offset]
                    else:
                        sql = "select %s from (" % return_fields_str + execute_sql + ") t %s LIMIT %%s OFFSET 0 " % sort_for_sql(sort)  # 第一页
                        limit_offset = [per_page]
                    data = connect_db.get_json(sql, [int(v) for v in limit_offset])
                else:
                    execute_sql += ' ' + sort_for_sql(sort)
                    data = connect_db.get_json(execute_sql, [int(v) for v in limit_offset])
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
                limit_offset = []
                if per_page != "ALL":
                    if page:
                        if limit:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [limit, (int(page) - 1) * int(limit)]
                        else:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [per_page, (int(page) - 1) * int(per_page)]
                    elif offset:
                        if limit:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [limit, offset]
                        else:
                            sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %%s OFFSET %%s " % sort_for_sql(sort)
                            limit_offset = [per_page, offset]
                    else:
                        sql = "select %s from (" % return_fields_str + sql + ") t %s LIMIT %%s OFFSET 0 " % sort_for_sql(sort)
                        limit_offset = [per_page]
                data = connect_db.get_json(sql, [int(v) for v in limit_offset])     # 返回目标表
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

